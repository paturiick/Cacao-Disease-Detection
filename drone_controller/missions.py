import threading
import time
from dataclasses import dataclass
from typing import List
from .client import TelloClient

@dataclass
class MissionStep:
    cmd: str
    delay_s: float = 1.0

class MissionBuilder:
    def __init__(self):
        self.steps: List[MissionStep] = []

    def takeoff(self, delay_s: float = 3.0):
        self.steps.append(MissionStep("takeoff", delay_s))
        return self

    def land(self, delay_s: float = 1.0):
        self.steps.append(MissionStep("land", delay_s))
        return self

    # --- Directional Commands (Limits: 20 to 500 cm) ---
    def forward_cm(self, cm: int, delay_s: float = 1.0):
        val = max(20, min(500, cm))
        self.steps.append(MissionStep(f"forward {val}", delay_s))
        return self

    def back_cm(self, cm: int, delay_s: float = 1.0):
        val = max(20, min(500, cm))
        self.steps.append(MissionStep(f"back {val}", delay_s))
        return self

    def left_cm(self, cm: int, delay_s: float = 1.0):
        val = max(20, min(500, cm))
        self.steps.append(MissionStep(f"left {val}", delay_s))
        return self

    def right_cm(self, cm: int, delay_s: float = 1.0):
        val = max(20, min(500, cm))
        self.steps.append(MissionStep(f"right {val}", delay_s))
        return self

    def up_cm(self, cm: int, delay_s: float = 1.0):
        val = max(20, min(500, cm))
        self.steps.append(MissionStep(f"up {val}", delay_s))
        return self

    def down_cm(self, cm: int, delay_s: float = 1.0):
        val = max(20, min(500, cm))
        self.steps.append(MissionStep(f"down {val}", delay_s))
        return self

    # --- Rotational Commands (Limits: 1 to 360 degrees) ---
    def cw_deg(self, deg: int, delay_s: float = 1.0):
        val = max(1, min(360, deg))
        self.steps.append(MissionStep(f"cw {val}", delay_s))
        return self

    def ccw_deg(self, deg: int, delay_s: float = 1.0):
        val = max(1, min(360, deg))
        self.steps.append(MissionStep(f"ccw {val}", delay_s))
        return self
        
    # --- Advanced Commands ---
    def hover(self, delay_s: float = 1.0):
        self.steps.append(MissionStep("stop", delay_s))
        return self

    def mon(self, delay_s: float = 1.0):
        self.steps.append(MissionStep("mon", delay_s))
        return self

    def moff(self, delay_s: float = 1.0):
        self.steps.append(MissionStep("moff", delay_s))
        return self

    def go_xyz(self, x: int, y: int, z: int, speed: int = 10, delay_s: float = 1.0):
        x_val = max(-500, min(500, x))
        y_val = max(-500, min(500, y))
        z_val = max(-500, min(500, z))
        spd_val = max(10, min(100, speed))
        
        if -20 < x_val < 20 and -20 < y_val < 20 and -20 < z_val < 20:
            x_val = 20 
            
        self.steps.append(MissionStep(f"go {x_val} {y_val} {z_val} {spd_val}", delay_s))
        return self

    # ==========================================
    # NEW: RC AUTOMATION COMMAND
    # ==========================================
    def rc(self, a: int, b: int, c: int, d: int, duration_s: float = 5.0):
        """
        Automates continuous RC flight. 
        a: roll, b: pitch, c: throttle, d: yaw (-100 to 100)
        duration_s: How long to hold the virtual sticks in this position
        """
        a_val = max(-100, min(100, int(a)))
        b_val = max(-100, min(100, int(b)))
        c_val = max(-100, min(100, int(c)))
        d_val = max(-100, min(100, int(d)))
        
        # We append 'delay_s' as the flight duration for the executor to use
        self.steps.append(MissionStep(f"rc {a_val} {b_val} {c_val} {d_val}", float(duration_s)))
        return self


class MissionExecutor:
    def __init__(self, client: TelloClient):
        self.client = client
        self._lock = threading.Lock()
        self.state = {
            "status": "inactive",
            "active_index": -1,
            "message": ""
        }
        self._thread = None
        self._cancel_flag = False

    @property
    def safe_state(self):
        with self._lock:
            return dict(self.state)

    def run_async(self, steps: List[MissionStep], speed: int = 10) -> tuple[bool, str]:
        if self.state["status"] == "running":
            return False, "Mission is already active."

        self._cancel_flag = False
        # Use daemon=True so the thread dies if the main app crashes
        self._thread = threading.Thread(target=self._execute_sequence, args=(steps, speed), daemon=True)
        self._thread.start()
        return True, "Mission sequence dispatched."

    def cancel(self):
        self._cancel_flag = True

    def _execute_sequence(self, steps: List[MissionStep], speed: int):
        try:
            self.state["status"] = "running"
       
            # 1. INITIAL TAKEOFF
            self.state["message"] = "Initiating Takeoff..."
            self.client.send("takeoff")
            # Wait longer for takeoff to stabilize before moving
            time.sleep(5.0) 

            # ==========================================
            # 2. SET DYNAMIC HARDWARE SPEED
            # ==========================================
            # Ensure speed is strictly within Tello's 10-100 cm/s limit
            safe_speed = max(10, min(100, speed))
            self.state["message"] = f"Setting flight speed to {safe_speed} cm/s..."
            
            print(f"\n[MISSION CONTROL] Setting hardware speed to {safe_speed} cm/s", flush=True)
            response = self.client.send(f"speed {safe_speed}")
            print(f"[DRONE RESPONSE] Speed set: {response.text}", flush=True)
            time.sleep(1.0) # Brief pause to let drone process the setting
            # ==========================================

            # 3. EXECUTE QUEUE
            for i, step in enumerate(steps):
                if self._cancel_flag:
                    self.state["status"] = "cancelled"
                    self.state["message"] = "Mission aborted by user."
                    self.client.send("land")
                    return

                self.state["active_index"] = i
                self.state["message"] = f"Step {i+1}/{len(steps)}: {step.cmd}"
                
                print(f"\n[MISSION CONTROL] Sending Command: {step.cmd}", flush=True)

                # ====================================================
                # NEW: AUTOMATED RC COMMANDS (Fire-and-forget loop)
                # ====================================================
                if step.cmd.startswith("rc "):
                    end_time = time.time() + step.delay_s
                    
                    # Heartbeat Loop: Send the command 10 times a second
                    while time.time() < end_time:
                        if self._cancel_flag:
                            break
                        try:
                            # Send directly via UDP socket so it doesn't block waiting for 'ok'
                            self.client.sock.sendto(step.cmd.encode("utf-8"), self.client.addr)
                        except Exception:
                            pass
                        time.sleep(0.1) 
                    
                    # Lookahead Logic: Are we chaining another RC command next?
                    is_next_rc = False
                    if i + 1 < len(steps):
                        if steps[i + 1].cmd.startswith("rc "):
                            is_next_rc = True
                    
                    # If the next step is NOT an RC command, slam the brakes.
                    if not is_next_rc and not self._cancel_flag:
                        try:
                            self.client.sock.sendto(b"rc 0 0 0 0", self.client.addr)
                        except Exception:
                            pass
                        time.sleep(0.5) # Brief pause to let the drone stabilize

                # ====================================================
                # STANDARD DISCRETE COMMANDS (Blocking)
                # ====================================================
                else:
                    response = self.client.send(step.cmd)
                    print(f"[DRONE RESPONSE] Tello replied: {response.text}\n", flush=True) 
                    
                    if not response or not getattr(response, 'ok', False):
                         raise Exception(f"Drone rejected command: {step.cmd}")

                    time.sleep(max(2.0, step.delay_s)) 

            self.state["status"] = "completed"
            self.state["message"] = "Mission complete. Executing landing."
            self.client.send("land")

        except Exception as e:
            self.state["status"] = "failed"
            self.state["message"] = f"Hardware Error: {str(e)}"
            # Try to land on failure if the drone is still connected
            try:
                self.client.send("land")
            except:
                pass
        finally:
            self.state["active_index"] = -1