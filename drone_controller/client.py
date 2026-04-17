import socket
import threading
import time
from dataclasses import dataclass
from .config import TELLO_IP, CMD_PORT, LOCAL_CMD_PORT, CMD_TIMEOUT_S
from .errors import DroneTimeout

@dataclass
class DroneReply:
    ok: bool
    text: str
    ms: int

class TelloClient:
    
    def __init__(self, tello_ip: str = TELLO_IP):
        self.addr = (tello_ip, CMD_PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", LOCAL_CMD_PORT))
        self.sock.settimeout(CMD_TIMEOUT_S)

        self._lock = threading.Lock()
        self._connected = False
        self._last = {"cmd": None, "res": None, "ts": None}

        self._heartbeat_thread = None
        self._stop_heartbeat = threading.Event()

    def connect(self) -> DroneReply:
        reply = self.send("command")
        if not reply.ok:
            return reply
        
        time.sleep(0.5)
        print("[CLIENT] Initializing Expansion Kit...")
        self.send("[TELLO]", timeout=1.0) 
        
        return reply
    
    def start_heartbeat(self):
        """Prevents the 15-second SDK timeout drop."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return
            
        self._stop_heartbeat.clear()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        print("[CLIENT] Heartbeat started.")

    def stop_heartbeat(self):
        self._stop_heartbeat.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=1.0)

    def _heartbeat_loop(self):
        """Sends a lightweight command every 10 seconds to keep the connection alive."""
        while not self._stop_heartbeat.is_set():
            time.sleep(10)
            if self._connected:
                try:
                    self.sock.sendto(b"sn?", self.addr)
                except Exception:
                    pass

    def send(self, cmd: str, timeout: float = None) -> DroneReply:
        """Sends a command to the Tello and waits for a specific 'ok' or 'error' response."""
        t0 = time.time()

        wait_time = timeout if timeout is not None else CMD_TIMEOUT_S

        # 1. Clear the buffer of any old data
        self.sock.setblocking(False)
        try:
            while True:
                # Keep reading until the buffer is empty
                data, _ = self.sock.recvfrom(1024)
        except (BlockingIOError, socket.error):
            # Buffer is now empty, proceed to send the new command
            pass 
        finally:
            # Re-enable blocking mode for the actual response wait
            self.sock.settimeout(wait_time)

        with self._lock:
            self._last["cmd"] = cmd
            self._last["ts"] = t0

        try:
            # 2. SEND COMMAND
            self.sock.sendto(cmd.encode("utf-8"), self.addr)
        except OSError as e:
            with self._lock:
                self._last["res"] = f"send error: {e}"
            self._connected = False
            return DroneReply(ok=False, text=f"send error: {e}", ms=int((time.time() - t0) * 1000))

        # 3. SMART WAIT LOOP (Filters out ESP32 GPS data)
        deadline = time.time() + wait_time
        while time.time() < deadline:
            try:
                data, _ = self.sock.recvfrom(1024)
            except ConnectionResetError:
                # Handle Windows-specific unreachable error (ICMP Port Unreachable)
                with self._lock:
                    self._last["res"] = "unreachable (WinError 10054)"
                self._connected = False
                return DroneReply(
                    ok=False, 
                    text="unreachable (WinError 10054): check Wi-Fi connection", 
                    ms=int((time.time() - t0) * 1000)
                )
            except socket.timeout:
                break # Exit the loop and trigger the DroneTimeout below
            except Exception:
                continue

            # Decode the response
            res = data.decode("utf-8", errors="ignore").strip()

            # --- THE FIX: IGNORE GPS NOISE ---
            if res.startswith("loc:") or res.startswith("sch:") or res.startswith("0TQ"):
                continue

            # 4. PARSE REAL DRONE RESPONSE
            dt_ms = int((time.time() - t0) * 1000)

            # Success if it says 'ok', or if it's the initial 'command' setup
            ok = (res.lower() == "ok") or (cmd == "command" and bool(res))
            
            if cmd == "command" and res:
                self._connected = True

            with self._lock:
                self._last["res"] = res

            return DroneReply(ok=ok, text=res, ms=dt_ms)

        # 5. IF WE RUN OUT OF TIME IN THE LOOP:
        raise DroneTimeout(f"Timeout waiting reply for cmd={cmd!r}")

    def status(self) -> dict:
        with self._lock:
            return {
                "connected": self._connected,
                "last_cmd": self._last["cmd"],
                "last_res": self._last["res"],
                "last_ts": self._last["ts"],
            }