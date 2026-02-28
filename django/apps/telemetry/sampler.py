import threading
import time
from datetime import timedelta
from django.utils import timezone
from django.db import close_old_connections

from apps.drone_runtime.services import status as runtime_status, telemetry as runtime_telemetry
from .models import TelemetrySnapshot

_started = False
_lock = threading.Lock()

def start_sampler(sample_every_s: float = 1.0):
    global _started
    with _lock:
        if _started:
            return
        _started = True

    def loop():
        while True:
            try:
                close_old_connections()
                
                s = runtime_status()
                t = runtime_telemetry()
                
                is_connected = bool(s.get("connected", False))
                
                if is_connected:
                    TelemetrySnapshot.objects.create(
                        connected=True,
                        battery=_safe_int(t.get("battery")),
                        altitude_m=_safe_float(t.get("alt_m")),
                        
                        # Orientation
                        pitch=_safe_int(t.get("pitch")),
                        roll=_safe_int(t.get("roll")),
                        yaw=_safe_int(t.get("yaw")),
                        
                        # Environment & Distance
                        tof_cm=_safe_int(t.get("tof_cm")),
                        temp_c=_safe_int(t.get("temp_c")),
                        templ_c=_safe_int(t.get("templ_c")),
                        baro=_safe_float(t.get("baro")),
                        
                        # Motion
                        vgx=_safe_int(t.get("vgx")),
                        vgy=_safe_int(t.get("vgy")),
                        vgz=_safe_int(t.get("vgz")),
                        agx=_safe_float(t.get("agx")),
                        agy=_safe_float(t.get("agy")),
                        agz=_safe_float(t.get("agz")),
                        
                        # Time & GPS
                        flight_time=_safe_int(t.get("flight_time")),
                        gps_lat=_safe_float(t.get("gps_lat")),
                        gps_lon=_safe_float(t.get("gps_lon")),
                        
                        raw=str(t.get("raw", "")),
                    )
                    
                    # 2. AUTO-CLEANUP (The Clearance): 
                    # Delete any flight data older than 1 hour
                    cutoff = timezone.now() - timedelta(hours=1)
                    TelemetrySnapshot.objects.filter(recorded_at__lt=cutoff).delete()

            except Exception:
                # Silently catch errors so the background thread never crashes
                pass
            
            # Sleep until the next sample is due
            time.sleep(max(0.2, float(sample_every_s)))

    # Start the loop in a background daemon thread
    threading.Thread(target=loop, daemon=True).start()

def _safe_int(x):
    try:
        return None if x is None else int(float(x))
    except Exception:
        return None

def _safe_float(x):
    try:
        return None if x is None else float(x)
    except Exception:
        return None