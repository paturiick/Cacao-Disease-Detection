import socket
import threading
import time
import select
from .config import LOCAL_STATE_PORT, LOCAL_GPS_PORT, LOCAL_CMD_PORT

class TelemetryReceiver:
    def __init__(self):
        self._stop = threading.Event()
        self._lock = threading.Lock()

        self.current_session_id = None
        
        self._state = {
            "battery": 0, "alt_m": 0.0,
            "pitch": 0, "roll": 0, "yaw": 0,
            "tof_cm": 0, "temp_c": 0, "templ_c": 0,
            "vgx": 0, "vgy": 0, "vgz": 0,          
            "agx": 0.0, "agy": 0.0, "agz": 0.0,    
            "baro": 0.0,                           
            "flight_time": 0,                      
            "gps_lat": 0.0, "gps_lon": 0.0, 
            "gps_sats": 0, "gps_status": "searching",
            "esp32_rssi": 0, "drone_snr": 0,
            "raw": "", "updated_at": None
        }

        # 1. Socket for Standard Drone Telemetry (Port 8890)
        self.state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.state_sock.bind(("", LOCAL_STATE_PORT))

        # 2. Socket for Custom ESP32 GPS Broadcasts (Port 8889)
        self.gps_sock = None 
        self.sockets_list = [self.state_sock]
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        # Prevent duplicate starts if it's currently running
        if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
            return

        # 1. Clear the kill switch
        self._stop.clear()

        # 2. Force close and rebuild the state socket
        if hasattr(self, 'state_sock') and self.state_sock:
            try: 
                self.state_sock.close() 
            except Exception: 
                pass
        self.state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.state_sock.bind(("", LOCAL_STATE_PORT))

        # 3. Force close and rebuild the GPS/ESP32 socket
        if hasattr(self, 'gps_sock') and self.gps_sock:
            try: 
                self.gps_sock.close() 
            except Exception: 
                pass
        self.gps_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.gps_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.gps_sock.bind(("", LOCAL_GPS_PORT))

        self.sockets_list = [self.state_sock, self.gps_sock]

        # 4. Boot a fresh thread
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        
        if self.thread.is_alive():
            self.thread.join(timeout=1.5)

        try:
            self.state_sock.close()
            self.gps_sock.close()
        except Exception as e:
            print(f"Error closing sockets: {e}")

    def _parse(self, msg: str) -> dict:
        out = {}
        for part in msg.strip().split(";"):
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            out[k] = v
        return out

    def _run(self):
        last_snr_poll = 0

        try:
            while not self._stop.is_set():
                
                current_time = time.time()
                if current_time - last_snr_poll > 2.0: # Poll every 2 seconds
                    try:
                        self.gps_sock.sendto(b"wifi?", ("192.168.10.1", LOCAL_CMD_PORT))
                        last_snr_poll = current_time
                    except Exception:
                        pass    



                # Use select to listen to BOTH sockets concurrently with a 1-second timeout
                read_sockets, _, _ = select.select(self.sockets_list, [], [], 1.0)

                for notified_socket in read_sockets:
                    data, _ = notified_socket.recvfrom(2048)
                    msg = data.decode("utf-8", errors="ignore").strip()

                    # ==========================================
                    # PATH A: ESP32 GPS DATA (Port 8889)
                    # ==========================================
                    if notified_socket == self.gps_sock:
                        with self._lock:
                            if msg.startswith("loc:"):
                                coords = msg.split("loc:")[1].split(",")
                                try:

                                    if len(coords) > 2:
                                        self._state["esp32_rssi"] = int(coords[2])

                                    self._state["gps_lat"] = float(coords[0])
                                    self._state["gps_lon"] = float(coords[1])
                                    self._state["gps_status"] = "locked"
                                except ValueError:
                                    pass
                            elif msg.startswith("sch:"):
                                parts = msg.split("sch:")[1].split(",")
                                try:
                                    self._state["gps_sats"] = int(parts[0])
                                    
                                    # Catch the RSSI if it exists
                                    if len(parts) > 1:
                                        self._state["esp32_rssi"] = int(parts[1])
                                        
                                    if self._state["gps_status"] != "locked":
                                        self._state["gps_status"] = "searching"
                                except ValueError:
                                    pass

                            elif msg.isdigit():
                                self.state["drone_snr"] = int(msg)    

                    # ==========================================
                    # PATH B: STANDARD FLIGHT DATA (Port 8890)
                    # ==========================================
                    elif notified_socket == self.state_sock:
                        d = self._parse(msg)

                        try:
                            bat = int(float(d.get("bat", 0)))
                            alt_m = float(d.get("h", 0)) / 100.0
                            pitch = int(float(d.get("pitch", 0)))
                            roll = int(float(d.get("roll", 0)))
                            yaw = int(float(d.get("yaw", 0)))
                            tof_cm = int(float(d.get("tof", 0)))
                            temp_c = int(float(d.get("temph", 0)))
                            templ_c = int(float(d.get("templ", 0)))
                            
                            vgx = int(float(d.get("vgx", 0)))
                            vgy = int(float(d.get("vgy", 0)))
                            vgz = int(float(d.get("vgz", 0)))
                            agx = float(d.get("agx", 0))
                            agy = float(d.get("agy", 0))
                            agz = float(d.get("agz", 0))
                            baro = float(d.get("baro", 0))
                            flight_time = int(float(d.get("time", 0)))
                        except Exception:
                            bat, alt_m, pitch, roll, yaw, tof_cm, temp_c, templ_c = 0, 0.0, 0, 0, 0, 0, 0, 0
                            vgx, vgy, vgz, agx, agy, agz, baro, flight_time = 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0


                        with self._lock:
                            self._state.update({
                                "battery": bat, "alt_m": alt_m,
                                "pitch": pitch, "roll": roll, "yaw": yaw,
                                "tof_cm": tof_cm, "temp_c": temp_c, "templ_c": templ_c,
                                "vgx": vgx, "vgy": vgy, "vgz": vgz,
                                "agx": agx, "agy": agy, "agz": agz,
                                "baro": baro, "flight_time": flight_time,
                                "raw": msg, "updated_at": time.time(),
                            })
        finally:
            try:
                self.state_sock.close()
                self.gps_sock.close()
            except Exception:
                pass

    def get(self) -> dict:
        with self._lock:
            return dict(self._state)