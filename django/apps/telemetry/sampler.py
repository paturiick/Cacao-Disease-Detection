import threading
import time
from datetime import timedelta
from django.utils import timezone
from django.db import close_old_connections

# FIX: Import the active hardware singletons!
from drone_controller.instance import get_drone_client, get_telemetry_receiver
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
                
                # FIX: Fetch from the active singletons
                client = get_drone_client()
                telemetry = get_telemetry_receiver()
                
                # Check connection status directly from the client
                is_connected = client.status().get("connected", False)
                
                if is_connected:
                    # Get the live dictionary from telemetry.py
                    t = telemetry.get()
                    
                    # Persist Snapshot
                    TelemetrySnapshot.objects.create(
                        connected=True,
                        battery=_safe_int(t.get("battery")),
                        altitude_m=_safe_float(t.get("alt_m")),
                        pitch=_safe_int(t.get("pitch")),
                        roll=_safe_int(t.get("roll")),
                        yaw=_safe_int(t.get("yaw")),
                        tof_cm=_safe_int(t.get("tof_cm")),
                        temp_c=_safe_int(t.get("temp_c")),
                        templ_c=_safe_int(t.get("templ_c")),
                        baro=_safe_float(t.get("baro")),
                        vgx=_safe_int(t.get("vgx")),
                        vgy=_safe_int(t.get("vgy")),
                        vgz=_safe_int(t.get("vgz")),
                        agx=_safe_float(t.get("agx")),
                        agy=_safe_float(t.get("agy")),
                        agz=_safe_float(t.get("agz")),
                        flight_time=_safe_int(t.get("flight_time")),
                        gps_lat=_safe_float(t.get("gps_lat")),
                        gps_lon=_safe_float(t.get("gps_lon")),
                        raw=str(t.get("raw", "")),
                    )
                    
                    cutoff = timezone.now() - timedelta(hours=1)
                    TelemetrySnapshot.objects.filter(recorded_at__lt=cutoff).delete()

            except Exception as e:
                pass
            
            time.sleep(max(0.2, float(sample_every_s)))

    threading.Thread(target=loop, daemon=True).start()

def _safe_int(x):
    try:
        return None if x is None else int(float(x))
    except (ValueError, TypeError):
        return None

def _safe_float(x):
    try:
        return None if x is None else float(x)
    except (ValueError, TypeError):
        return None