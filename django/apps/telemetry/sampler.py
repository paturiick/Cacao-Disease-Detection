import threading
import time
from datetime import timedelta
from django.utils import timezone
from django.db import close_old_connections
from django.db.models import Q

from drone_controller.instance import get_drone_client, get_telemetry_receiver
from .models import TelemetrySnapshot, MissionTelemetryLog

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
        
        # Initialize telemetry receiver and start the listener immediately to catch ESP32 data
        telemetry = get_telemetry_receiver()
        if not telemetry.thread.is_alive():
            print("[TELEMETRY] Booting Port 8891 Listener...")
            telemetry.start()
        else:
            print("SAMPLER STARTUP FAILED")
            return

        last_snr_check = 0

        while True:
            try:
                # Refresh database connections for this background thread
                close_old_connections()
                
                client = get_drone_client()
                is_connected = client.status().get("connected", False)
                
                # Define current_time here so it is accessible throughout the loop iteration
                current_time = time.time()

                # --- 1. Drone-Specific Logic (Only if Synced) ---
                if is_connected:
                    # Periodic SNR check (every 3 seconds)
                    if current_time - last_snr_check > 3.0:
                        try:
                            reply = client.send("wifi?", timeout=0.5)
                            print(f"[DEBUG SNR] Drone replied to wifi?: '{reply.text}'", flush=True)
                            # Stop checking if reply.ok is True, just parse the text
                            if reply.text:
                                try:
                                    # Strip whitespace and handle potential negative numbers/formatted strings
                                    snr_value = int(float(reply.text.strip())) 
                                    with telemetry._lock:
                                        # Absolute value used for consistent UI representation
                                        telemetry._state["drone_snr"] = abs(snr_value) 
                                except (ValueError, TypeError):
                                    pass
                        except Exception:
                            # Catch DroneTimeout so it doesn't abort the snapshot save!
                            pass
                        
                        last_snr_check = current_time

                # --- 2. Always Create Snapshot ---
                # This ensures ESP32 RSSI and GPS data are visible even if the drone is off
                t = telemetry.get()
                
                TelemetrySnapshot.objects.create(
                    connected=is_connected,
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
                    gps_sats=_safe_int(t.get("gps_sats")),
                    gps_status=str(t.get("gps_status", "searching")),

                    drone_snr=_safe_int(t.get("drone_snr")),
                    esp32_rssi=_safe_int(t.get("esp32_rssi")),
                    
                    raw=str(t.get("raw", "")),
                )

                # --- 3. Mission Logging (Active Sessions Only) ---
                if is_connected and telemetry.current_session_id:
                    MissionTelemetryLog.objects.create(
                        session_id=telemetry.current_session_id,
                        battery=_safe_int(t.get("battery")),
                        altitude_m=_safe_float(t.get("alt_m")),
                        flight_time=_safe_int(t.get("flight_time")),
                        pitch=_safe_int(t.get("pitch")),
                        roll=_safe_int(t.get("roll")),
                        yaw=_safe_int(t.get("yaw")),
                        temp_c=_safe_int(t.get("temp_c")),
                        gps_lat=_safe_float(t.get("gps_lat")),
                        gps_lon=_safe_float(t.get("gps_lon"))
                    )
                
                # --- 4. Database Cleanup ---
                # Automatically delete snapshots older than one hour to maintain performance
                cutoff = timezone.now() - timedelta(hours=1)
                TelemetrySnapshot.objects.filter(
                    Q(recorded_date__lt=cutoff.date()) | 
                    Q(recorded_date=cutoff.date(), recorded_time__lt=cutoff.time())
                ).delete()

            except Exception as e:
                print(f"SAMPLER CRASHED: {e}") 
            
            # Maintain the specified sampling interval
            time.sleep(max(0.2, float(sample_every_s)))

    # Start the daemon thread
    t = threading.Thread(target=loop, daemon=True)
    t.start()

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