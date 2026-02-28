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

        self.sock.bind(("", LOCAL_CMD_PORT))
        self.sock.settimeout(CMD_TIMEOUT_S)

        self._lock = threading.Lock()
        self._connected = False
        self._last = {"cmd": None, "res": None, "ts": None}

    def connect(self) -> DroneReply:
        return self.send("command")

    def send(self, cmd: str) -> DroneReply:
        t0 = time.time()
        with self._lock:
            self._last["cmd"] = cmd
            self._last["ts"] = t0

        try:
            self.sock.sendto(cmd.encode("utf-8"), self.addr)
        except OSError as e:
            with self._lock:
                self._last["res"] = f"send error: {e}"
            self._connected = False
            return DroneReply(ok=False, text=f"send error: {e}", ms=int((time.time() - t0) * 1000))

        try:
            data, _ = self.sock.recvfrom(1024)
        except ConnectionResetError:
            # UDP: ICMP "Port unreachable" becomes WinError 10054 here
            with self._lock:
                self._last["res"] = "unreachable (WinError 10054)"
            self._connected = False
            return DroneReply(ok=False, text="unreachable (WinError 10054): not on drone Wi-Fi / wrong IP / drone not ready", ms=int((time.time() - t0) * 1000))
        except socket.timeout:
            raise DroneTimeout(f"Timeout waiting reply for cmd={cmd!r}")

        res = data.decode("utf-8", errors="ignore").strip()
        dt_ms = int((time.time() - t0) * 1000)

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