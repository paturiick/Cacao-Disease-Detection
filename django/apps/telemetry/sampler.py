import threading
import time
from datetime import timedelta
from django.utils import timezone
from django.db import close_old_connections
from django.db.models import Q

from drone_controller.instance import get_drone_client, get_telemetry_receiver
from .models import TelemetrySnapshot, LiveSystemState, MissionTelemetryLog

_started = False
_lock = threading.Lock()

def start_sampler(sample_every_s: float = 1.0):
    global _started
    with _lock:
        if _started:
            return
        _started = True

    def loop():
        print("SAMPLER THREAD STARTED!")
        while True:
            try:
                close_old_connections()
                
                client = get_drone_client()
                telemetry = get_telemetry_receiver()
                
                is_connected = client.status().get("connected", False)
                
                # Fetch the live state directly from Postgres
                state, _ = LiveSystemState.objects.get_or_create(id=1)
                
                #print(f"Connected: {is_connected} | GPS: {state.gps_lat}, {state.gps_lon} | BLE Active: {state.ble_active}")
                
                if is_connected:
                    t = telemetry.get()
                    
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
                        
                        # INJECT GPS FROM POSTGRES HERE:
                        gps_lat=state.gps_lat,
                        gps_lon=state.gps_lon,
                        
                        raw=str(t.get("raw", "")),
                    )

                    if telemetry.current_session_id:
                        MissionTelemetryLog.objects.create(
                            session_id=telemetry.current_session_id,
                            battery=_safe_int(t.get("battery")),
                            altitude_m=_safe_float(t.get("alt_m")),
                            flight_time=_safe_int(t.get("flight_time")),
                            pitch=_safe_int(t.get("pitch")),
                            roll=_safe_int(t.get("roll")),
                            yaw=_safe_int(t.get("yaw")),
                            temp_c=_safe_int(t.get("temp_c")),
                            gps_lat=state.gps_lat,
                            gps_lon=state.gps_lon
                        )
                    
                    cutoff = timezone.now() - timedelta(hours=1)
                    TelemetrySnapshot.objects.filter(
                        Q(recorded_date__lt=cutoff.date()) | 
                        Q(recorded_date=cutoff.date(), recorded_time__lt=cutoff.time())
                    ).delete()

            except Exception as e:
                print(f"SAMPLER CRASHED: {e}") 
            
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