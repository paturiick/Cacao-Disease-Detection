import socket
import threading
from django.utils import timezone
from .models import MissionPlan

def parse_kv(s: str):
    """Parses drone state string into a dictionary."""
    out = {}
    for part in s.strip().split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k] = v
    return out

def _telemetry_listener():
    # Fixed: sock is explicitly defined here
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("", 8890))
        sock.settimeout(1.5)
        print("[*] Telemetry Listener Started")
    except Exception as e:
        print(f"[!] Bind Error: {e}")
        return

    while True:
        try:
            data, _ = sock.recvfrom(2048)
            state = parse_kv(data.decode("utf-8", errors="ignore"))
            
            # Update DB - This makes the NavBar turn GREEN
            MissionPlan.objects.all().update(
                battery=int(state.get("bat", 0)),
                gps="Connected",
                updated_at=timezone.now()
            )
        except socket.timeout:
            # Mark as disconnected if no data received
            MissionPlan.objects.filter(gps="Connected").update(gps="Disconnected")
        except Exception:
            continue

def start_telemetry_worker():
    thread = threading.Thread(target=_telemetry_listener, daemon=True)
    thread.start()