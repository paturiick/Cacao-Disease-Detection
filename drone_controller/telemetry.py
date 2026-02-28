import socket
import threading
import time
from .config import LOCAL_STATE_PORT

class TelemetryReceiver:
    def __init__(self):
        self._stop = threading.Event()
        self._lock = threading.Lock()
        
        self._state = {
            "battery": 0, "alt_m": 0.0,
            "pitch": 0, "roll": 0, "yaw": 0,
            "tof_cm": 0, "temp_c": 0, "templ_c": 0,
            "vgx": 0, "vgy": 0, "vgz": 0,          # Velocity X, Y, Z
            "agx": 0.0, "agy": 0.0, "agz": 0.0,    # Acceleration X, Y, Z
            "baro": 0.0,                           # Barometer
            "flight_time": 0,                      # Motor run time
            "gps_lat": 0.0, "gps_lon": 0.0, 
            "raw": "", "updated_at": None
        }

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", LOCAL_STATE_PORT))
        self.sock.settimeout(1.0)

        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()

    def _parse(self, msg: str) -> dict:
        out = {}
        for part in msg.strip().split(";"):
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            out[k] = v
        return out

    def _run(self):
        while not self._stop.is_set():
            try:
                data, _ = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            
            msg = data.decode("utf-8", errors="ignore")
            d = self._parse(msg)

            # Parse ALL flight data safely
            try:
                bat = int(float(d.get("bat", 0)))
                alt_m = float(d.get("h", 0)) / 100.0
                pitch, roll, yaw = int(float(d.get("pitch", 0))), int(float(d.get("roll", 0))), int(float(d.get("yaw", 0)))
                tof_cm = int(float(d.get("tof", 0)))
                temp_c, templ_c = int(float(d.get("temph", 0))), int(float(d.get("templ", 0)))
                
                # New fields: Velocity, Acceleration, Baro, Time
                vgx, vgy, vgz = int(float(d.get("vgx", 0))), int(float(d.get("vgy", 0))), int(float(d.get("vgz", 0)))
                agx, agy, agz = float(d.get("agx", 0)), float(d.get("agy", 0)), float(d.get("agz", 0))
                baro = float(d.get("baro", 0))
                flight_time = int(float(d.get("time", 0)))
            except Exception:
                bat, alt_m, pitch, roll, yaw, tof_cm, temp_c, templ_c = 0, 0.0, 0, 0, 0, 0, 0, 0
                vgx, vgy, vgz, agx, agy, agz, baro, flight_time = 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0
                
            try:
                lat, lon = float(d.get("lat", 0.0)), float(d.get("lon", 0.0))
            except Exception:
                lat, lon = 0.0, 0.0

            with self._lock:
                self._state.update({
                    "battery": bat, "alt_m": alt_m,
                    "pitch": pitch, "roll": roll, "yaw": yaw,
                    "tof_cm": tof_cm, "temp_c": temp_c, "templ_c": templ_c,
                    "vgx": vgx, "vgy": vgy, "vgz": vgz,
                    "agx": agx, "agy": agy, "agz": agz,
                    "baro": baro, "flight_time": flight_time,
                    "gps_lat": lat, "gps_lon": lon,
                    "raw": msg, "updated_at": time.time(),
                })

    def get(self) -> dict:
        with self._lock:
            return dict(self._state)