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

        self.sock.settimeout(7.0)

        self.sock.bind(("", LOCAL_CMD_PORT))
        self.sock.settimeout(CMD_TIMEOUT_S)

        self._lock = threading.Lock()
        self._connected = False
        self._last = {"cmd": None, "res": None, "ts": None}

    def connect(self) -> DroneReply:
        return self.send("command")

    def send(self, cmd: str) -> DroneReply:
        """Sends a command to the Tello and waits for a specific 'ok' or 'error' response."""
        t0 = time.time()

        # 1. FLUSH RECEIVE BUFFER
        # We set to non-blocking to 'vacuum' any old data out of the socket
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
            self.sock.setblocking(True)

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

        try:
            # 3. WAIT FOR FRESH RESPONSE
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
            # Triggered if the drone doesn't reply within CMD_TIMEOUT_S
            raise DroneTimeout(f"Timeout waiting reply for cmd={cmd!r}")

        # 4. PARSE RESPONSE
        res = data.decode("utf-8", errors="ignore").strip()
        dt_ms = int((time.time() - t0) * 1000)

        # Success if it says 'ok', or if it's the initial 'command' setup
        ok = (res.lower() == "ok") or (cmd == "command" and bool(res))
        
        if cmd == "command" and res:
            self._connected = True

        with self._lock:
            self._last["res"] = res

        return DroneReply(ok=ok, text=res, ms=dt_ms)

    def status(self) -> dict:
        with self._lock:
            return {
                "connected": self._connected,
                "last_cmd": self._last["cmd"],
                "last_res": self._last["res"],
                "last_ts": self._last["ts"],
            }