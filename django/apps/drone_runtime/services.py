from apps.detections.inference import start_inference_loop
import time
from django.views.decorators.csrf import csrf_exempt
from drone_controller.instance import (
    get_drone_client, 
    get_video_receiver, 
    get_telemetry_receiver, 
    get_mission_executor
)


def connect():
    try:
        client = get_drone_client()
        
        reply = client.connect()  
        
        if reply.ok:
            get_telemetry_receiver().start()

            start_inference_loop()
            
            return {
                "ok": True, 
                "text": reply.text if reply.text else "SDK Mode Enabled",
                "ms": reply.ms
            }
        
        return {
            "ok": False, 
            "text": f"Connection Failed: {reply.text}", 
            "ms": reply.ms
        }
            
    except Exception as e:
        return {"ok": False, "text": f"System Error: {str(e)}", "ms": 0}

def status() -> dict:
    """Aggregates health data from the client and video domains."""
    client = get_drone_client()
    video = get_video_receiver()
    telemetry = get_telemetry_receiver()
    
    # Check if telemetry is still alive
    t_state = telemetry.get()
    last_update = t_state.get("updated_at")
    is_alive = last_update and (time.time() - last_update < 3.0)
    
    c_status = client.status()
    if not is_alive:
        # Update client connection state if telemetry heartbeats stop
        client._connected = False
        c_status["connected"] = False
    
    return {
        **c_status, 
        "video_last_frame_bytes": video.get_latest_frame_size() # New helper
    }

def telemetry() -> dict:
    """Returns ONLY the flight telemetry from the shared receiver."""
    return get_telemetry_receiver().get()

def send(cmd: str):
    """Sends a raw command string through the shared client."""
    return get_drone_client().send(cmd)

def stream_on():
    return get_drone_client().send("streamon")

def stream_off():
    return get_drone_client().send("streamoff")

def get_video_stream() -> bytes:
    """Returns the latest decoded JPEG frame for the live app."""
    return get_video_receiver().get_latest_frame()

def run_mission(steps: list) -> dict:
    """Passes steps to the singleton MissionExecutor."""
    client = get_drone_client()
    executor = get_mission_executor()
    
    if not client.status().get("connected"):
        return {"ok": False, "text": "Cannot start mission: Drone is disconnected."}
        
    try:
        # Passes flight plan to the executor logic
        result = executor.run(steps, ensure_stream=False)
        return {
            "ok": True, 
            "text": "Mission execution started", 
            "details": result
        }
    except Exception as e:
        return {"ok": False, "text": f"Mission failed to start: {str(e)}"}
    
def get_mission_progress() -> dict:
    """Queries the singleton executor for the current state."""
    client = get_drone_client()
    executor = get_mission_executor()
    
    state = executor.state
    if state["status"] == "running" and not client.status().get("connected"):
        state["status"] = "failed"
        state["message"] = "Drone disconnected during mission."
        executor.cancel()

    return {
        "status": state["status"],             
        "active_index": state["active_index"], 
        "message": state["message"]            
    }