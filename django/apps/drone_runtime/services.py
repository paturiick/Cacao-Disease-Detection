import threading
import time
from drone_controller.main import DroneBrain
from django.views.decorators.csrf import csrf_exempt

_lock = threading.Lock()
_inited = False

_brain: DroneBrain | None = None

def ensure_runtime():
    """Ensures the DroneBrain is instantiated exactly once."""
    global _inited, _brain
    with _lock:
        if _inited:
            return
        _brain = DroneBrain()
        _inited = True

def connect():
    ensure_runtime()
    try:
        # connect_and_initialize sends the "command" string to port 8889 [cite: 18, 42]
        success = _brain.connect_and_initialize()
        
        # Get status and provide a safe default for 'last_res'
        client_status = _brain.client.status()
        response_text = client_status.get("last_res")
        
        if success:
            # If success is True but last_res is empty, use a default 
            return {
                "ok": True, 
                "text": response_text if response_text else "Connected (OK)",
                "ms": 0
            }
        else:
            return {
                "ok": False, 
                "text": f"Drone Offline: {response_text}" if response_text else "Failed to connect", 
                "ms": 0
            }
            
    except Exception as e:
        if _brain:
            _brain.client._connected = False
        return {"ok": False, "text": f"System Error: {str(e)}", "ms": 0}

def status() -> dict:
    ensure_runtime()
    if not _brain:
        return {"connected": False, "text": "Not Initialized"}
        
    t = _brain.get_current_state()
    v = {"video_last_pkt_bytes": _brain.video.last_packet_size()}
    c = _brain.client.status()
    
    # Deadman's Switch logic: mark disconnected if no telemetry for 3 seconds
    last_update = t.get("updated_at")
    is_alive = last_update and (time.time() - last_update < 3.0)
            
    if not is_alive:
        _brain.client._connected = False  
        c["connected"] = False            
    
    return {**c, **v}

def telemetry() -> dict:
    """Returns ONLY the flight telemetry."""
    ensure_runtime()
    if not _brain:
        return {}
    return _brain.get_current_state()

def send(cmd: str):
    ensure_runtime()
    return _brain.client.send(cmd)

def stream_on():
    ensure_runtime()
    return _brain.client.send("streamon")

def stream_off():
    ensure_runtime()
    return _brain.client.send("streamoff")

def get_video_stream() -> bytes:
    ensure_runtime()
    if not _brain:
        return b""
    return _brain.get_video_stream()    