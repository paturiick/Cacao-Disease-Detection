from apps.drone_runtime.services import get_brain
from drone_controller.missions import MissionBuilder

def get_mission_progress() -> dict:
    """Polled by the frontend to move the UI progress bar."""
    brain = get_brain()
    
    
    if not brain:
        return {"status": "inactive", "active_index": -1, "message": "Hardware controller not initialized."}
        
    # Read the state directly from your MissionExecutor in the background thread
    state = brain.mission_executor.state
    return {
        "status": state["status"],             # 'running', 'completed', 'failed', 'cancelled'
        "active_index": state["active_index"], # e.g., 0, 1, 2...
        "message": state["message"]            # e.g., "Executing step 2: forward 100"
    }

def start_hardware_mission(steps_data: list, speed: int = 30) -> dict:
    """Takes database steps, translates them, and starts the flight thread."""
    brain = get_brain()
    
    # Safety check: don't start the mission if hardware is off or disconnected
    if not brain or not getattr(brain.client, '_connected', False):
        return {"ok": False, "text": "Drone is disconnected. Please Sync."}
        
    builder = MissionBuilder()
    
    # Translate frontend JSON strings to SDK builder methods
    for step in steps_data:
        cmd_type = step.get("type", "").lower()
        val_str = str(step.get("val", "0"))
        
        # Safely parse integer values
        try: 
            val = int(val_str)
        except ValueError: 
            val = 0
            
        # The MissionBuilder class automatically enforces SDK min/max limits (e.g., 20-500cm)
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
            # go command expects "x y z speed"
            parts = val_str.split()
            if len(parts) >= 3:
                builder.go_xyz(
                    int(parts[0]), 
                    int(parts[1]), 
                    int(parts[2]), 
                    int(parts[3]) if len(parts) == 4 else speed
                )

    # Trigger the background executor thread you built in drone_controller/missions.py
    success, text = brain.mission_executor.run_async(builder.steps, speed)
    return {"ok": success, "text": text}

def send_live_override(cmd: str) -> dict:
    """Instantly bypasses the queue for safety commands (Emergency, Force Land, Stop)."""
    brain = get_brain()
    
    if not brain or not getattr(brain.client, '_connected', False):
        return {"ok": False, "text": "Hardware disconnected."}
        
    # 1. Flag the background mission thread to abort its loop immediately
    brain.mission_executor.cancel()
    
    # 2. Fire the raw command directly to the UDP socket to halt the physical drone
    reply = brain.client.send(cmd)
    
    return {"ok": True if "error" not in reply.lower() else False, "text": reply}