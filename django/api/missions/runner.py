import threading
import time
import socket
from dataclasses import dataclass
from django.db import transaction
from django.utils import timezone  # Fixed: timezone import added
from .models import MissionPlan, MissionStep

@dataclass
class DroneResult:
    ok: bool
    message: str = ""

class TelloDroneController:
    """Real UDP controller for DJI RoboMaster TT."""
    def __init__(self, ip="192.168.10.1", port=8889):
        self.address = (ip, port)
        # Fixed: sock is properly initialized within the class
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5.0)

    def send(self, command: str) -> DroneResult:
        """Sends a command and waits for 'ok' response."""
        try:
            print(f"[DRONE] Sending: {command}")
            self.sock.sendto(command.encode('utf-8'), self.address)
            data, _ = self.sock.recvfrom(1024)
            response = data.decode('utf-8').strip()
            print(f"[DRONE] Received: {response}")
            return DroneResult(response == "ok", response)
        except socket.timeout:
            return DroneResult(False, "Timeout: No response from drone")
        except Exception as e:
            return DroneResult(False, str(e))

    def connect(self): return self.send("command")
    def stream_on(self): return self.send("streamon")
    def takeoff(self): return self.send("takeoff")
    def land(self): return self.send("land")
    
    def stop(self):
        """Zero out movement and wait for stabilization."""
        res = self.send("rc 0 0 0 0")
        time.sleep(0.3)
        return res

    def rc_step(self, roll: int, pitch: int, throttle: int, yaw: int):
        return self.send(f"rc {roll} {pitch} {throttle} {yaw}")

    def close(self):
        self.sock.close()

# Logic to prevent duplicate mission threads
_running_lock = threading.Lock()
_running_threads = {}

def _speed_to_rc(speed_m_s: float) -> int:
    try: v = float(speed_m_s)
    except: v = 1.0
    return max(10, min(100, int(v * 20)))

def start_plan(plan_id: int) -> bool:
    with _running_lock:
        t = _running_threads.get(plan_id)
        if t and t.is_alive(): return False
        thread = threading.Thread(target=_execute_plan, args=(plan_id,), daemon=True)
        _running_threads[plan_id] = thread
        thread.start()
        return True

def _set_plan(plan_id: int, **fields):
    with transaction.atomic():
        plan = MissionPlan.objects.select_for_update().get(id=plan_id)
        for k, v in fields.items():
            setattr(plan, k, v)
        plan.save()

def _execute_plan(plan_id: int):
    ctrl = TelloDroneController()
    # Fixed: timezone used to track start time
    _set_plan(plan_id, status="queued", message="Connecting...", updated_at=timezone.now())

    if not ctrl.connect().ok:
        _set_plan(plan_id, status="failed", message="No Drone Connection")
        return

    ctrl.stream_on()
    time.sleep(1)

    if not ctrl.takeoff().ok:
        _set_plan(plan_id, status="failed", message="Takeoff Failed")
        return

    steps = list(MissionStep.objects.filter(plan_id=plan_id).order_by("order", "id"))
    plan_config = MissionPlan.objects.get(id=plan_id)
    speed_rc = _speed_to_rc(plan_config.speed)

    for i, step in enumerate(steps, start=1):
        if MissionPlan.objects.get(id=plan_id).status == "cancelled":
            ctrl.land()
            return

        ctrl.stop() # Clear momentum before next move
        duration = max(0.5, float(step.val))
        _set_plan(plan_id, active_index=i, message=f"Moving {step.type}")

        if step.type == "left":       ctrl.rc_step(-speed_rc, 0, 0, 0)
        elif step.type == "right":    ctrl.rc_step(speed_rc, 0, 0, 0)
        elif step.type == "forward":  ctrl.rc_step(0, speed_rc, 0, 0)
        elif step.type == "back":     ctrl.rc_step(0, -speed_rc, 0, 0)
        elif step.type == "up":       ctrl.rc_step(0, 0, speed_rc, 0)
        elif step.type == "down":     ctrl.rc_step(0, 0, -speed_rc, 0)
        elif step.type == "cw":       ctrl.rc_step(0, 0, 0, speed_rc)
        elif step.type == "ccw":      ctrl.rc_step(0, 0, 0, -speed_rc)

        time.sleep(duration)
        ctrl.stop()

    ctrl.land()
    ctrl.close()
    _set_plan(plan_id, status="completed", active_index=-1, message="Success")

def trigger_emergency_land():
    """Sends the landing command immediately to the drone's IP."""
    TELLO_IP = "192.168.10.1"
    CMD_PORT = 8889
    
    # We use a separate one-off socket to ensure it isn't blocked 
    # by the main mission thread's timeout settings
    emergency_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 1. Zero out any active RC movements first
        emergency_sock.sendto(b"rc 0 0 0 0", (TELLO_IP, CMD_PORT))
        time.sleep(0.1)
        # 2. Command the land
        emergency_sock.sendto(b"land", (TELLO_IP, CMD_PORT))
        print("[!] EMERGENCY: Force Land command sent.")
    finally:
        emergency_sock.close()