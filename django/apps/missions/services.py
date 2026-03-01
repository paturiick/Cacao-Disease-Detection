from drone_controller.missions import MissionBuilder
from drone_controller.instance import (
    get_drone_client, 
    get_mission_executor
)

def get_mission_progress() -> dict:
    """Polled by the frontend to move the UI progress bar."""
    executor = get_mission_executor()
    
    # Read the state directly from your singleton MissionExecutor in the background thread
    state = executor.state
    return {
        "status": state["status"],             # 'running', 'completed', 'failed', 'cancelled'
        "active_index": state["active_index"], # e.g., 0, 1, 2...
        "message": state["message"]            # e.g., "Executing step 2: forward 100"
    }

def start_hardware_mission(steps_data: list, speed: int = 30) -> dict:
    """Takes database steps, translates them, and starts the flight thread."""
    client = get_drone_client()
    executor = get_mission_executor()
    
    # Safety check: Use the singleton client status to verify connection
    if not client.status().get("connected"):
        return {"ok": False, "text": "Drone is disconnected. Please Sync."}
        
    builder = MissionBuilder()
    
    # Translate frontend JSON strings to SDK builder methods
    for step in steps_data:
        cmd_type = step.get("type", "").lower()
        val_str = str(step.get("val", "0"))
        
        try: 
            val = int(val_str)
        except ValueError: 
            val = 0
            
        if cmd_type == "forward": builder.forward_cm(val)
        elif cmd_type == "back": builder.back_cm(val)
        elif cmd_type == "left": builder.left_cm(val)
        elif cmd_type == "right": builder.right_cm(val)
        elif cmd_type == "up": builder.up_cm(val)
        elif cmd_type == "down": builder.down_cm(val)
        elif cmd_type == "cw": builder.cw_deg(val)
        elif cmd_type == "ccw": builder.ccw_deg(val)
        elif cmd_type == "hover": builder.hover()
        elif cmd_type == "go":
            parts = val_str.split()
            if len(parts) >= 3:
                builder.go_xyz(
                    int(parts[0]), 
                    int(parts[1]), 
                    int(parts[2]), 
                    int(parts[3]) if len(parts) == 4 else speed
                )

    # Trigger the background executor thread using the singleton
    success, text = executor.run_async(builder.steps, speed)
    return {"ok": success, "text": text}

def send_live_override(cmd: str) -> dict:
    """Instantly bypasses the queue for safety commands."""
    client = get_drone_client()
    executor = get_mission_executor()
    
    if not client.status().get("connected"):
        return {"ok": False, "text": "Hardware disconnected."}
        
    # 1. Flag the singleton background mission thread to abort its loop immediately
    executor.cancel()
    
    # 2. Fire the raw command directly to the UDP socket to halt the physical drone
    reply = client.send(cmd)
    
    # Check reply text directly for errors
    is_ok = "error" not in str(reply.text).lower() if hasattr(reply, 'text') else False
    return {"ok": is_ok, "text": str(reply.text) if hasattr(reply, 'text') else "Override Sent"}