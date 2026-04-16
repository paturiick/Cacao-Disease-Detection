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
    
    if not client.status().get("connected"):
        return {"ok": False, "text": "Drone is disconnected. Please Sync."}
        
    builder = MissionBuilder()
    
    for step in steps_data:
        # FIXED: Check for both 'type' (from planner) and 'command' (from RC panel)
        cmd_type = step.get("type", step.get("command", "")).lower()
        val_str = str(step.get("val", step.get("value", "0")))
        
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
        elif cmd_type == "dumb": builder.dumb_wait(val)
        elif cmd_type == "hover": builder.hover()

        elif cmd_type in ["motor_on", "motoron"]: builder.motor_on(val if val > 0 else 1.0)
        elif cmd_type in ["motor_off", "motoroff"]: builder.motor_off(val if val > 0 else 1.0)
        
        # NEW: Added missing RC Control Panel mappings
        elif cmd_type == "takeoff": builder.takeoff()
        elif cmd_type == "land": builder.land()
        elif cmd_type == "rc":
            parts = val_str.split()
            if len(parts) >= 4:
                # Grab the movement forces
                a, b, c, d = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                
                duration = float(parts[4]) if len(parts) >= 5 else 5.0
                
                # Pass it to the builder
                builder.rc(a, b, c, d, duration_s=duration)
        elif cmd_type == "go":
            parts = val_str.split()
            if len(parts) >= 3:
                builder.go_xyz(
                    int(parts[0]), int(parts[1]), int(parts[2]), 
                    int(parts[3]) if len(parts) == 4 else speed
                )

    # FIXED: Check if this is a standard drawn mission or just a live RC override
    is_live_override = any(cmd in [s.get("command", "") for s in steps_data] for cmd in ["takeoff", "land", "rc"])
    
    if not is_live_override:
        # It's a standard drawn mission queue. Add the safe takeoff and landing brackets!
        builder.wrap_standard_flight()

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