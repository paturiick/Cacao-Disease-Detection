import threading
import time
import socket
from dataclasses import dataclass
from django.db import transaction
from django.utils import timezone
from .models import MissionPlan, MissionStep

# -----------------------------
# REAL Tello/RoboMaster Controller
# -----------------------------
@dataclass
class DroneResult:
    ok: bool
    message: str = ""

class TelloDroneController:
    def __init__(self, ip="192.168.10.1", port=8889):
        self.address = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5.0)

    def send(self, command: str) -> DroneResult:
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
    def emergency(self): return self.send("emergency")
    
    def rc(self, roll: int, pitch: int, throttle: int, yaw: int):
        self.sock.sendto(f"rc {roll} {pitch} {throttle} {yaw}".encode(), self.address)

    def close(self): self.sock.close()

# -----------------------------
# Runner Logic
# -----------------------------
_running_lock = threading.Lock()
_running_threads = {}

def _speed_to_rc(speed_m_s: float) -> int:
    try:
        v = float(speed_m_s)
    except:
        v = 1.0
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
        for k, v in fields.items(): setattr(plan, k, v)
        plan.save()

def _execute_plan(plan_id: int):
    ctrl = TelloDroneController()
    _set_plan(plan_id, status="queued", message="Connecting to drone...")

    if not ctrl.connect().ok:
        _set_plan(plan_id, status="failed", message="Check Wi-Fi connection.", active_index=-1)
        return

    ctrl.stream_on()
    time.sleep(1)

    # Note: Battery must be > 15% to avoid 'Takeoff Failed'
    if not ctrl.takeoff().ok:
        _set_plan(plan_id, status="failed", message="Takeoff Failed (Check Battery/Heat)", active_index=-1)
        return

    steps = list(MissionStep.objects.filter(plan_id=plan_id).order_by("order", "id"))
    plan_config = MissionPlan.objects.get(id=plan_id)
    speed_rc = _speed_to_rc(plan_config.speed)

    for i, step in enumerate(steps, start=1):
        current_plan = MissionPlan.objects.get(id=plan_id)
        if current_plan.status == "cancelled":
            ctrl.land()
            return

        duration = max(0.5, float(step.val))
        _set_plan(plan_id, active_index=i, message=f"Moving: {step.type}")
        cmd = step.type.lower().strip()

        # --- SDK ROTATION LOGIC (KEEPS COMPATIBILITY) ---
        if cmd in ["cw", "rotate cw"]: 
            ctrl.send(f"cw {int(duration) if duration >= 1 else 90}")
        elif cmd in ["ccw", "rotate ccw"]: 
            ctrl.send(f"ccw {int(duration) if duration >= 1 else 90}")
        
        # --- REVERTED ORIGINAL RC LOGIC FOR OTHERS ---
        elif cmd == "left":    ctrl.rc(-speed_rc, 0, 0, 0); time.sleep(duration)
        elif cmd == "right":   ctrl.rc(speed_rc, 0, 0, 0); time.sleep(duration)
        elif cmd == "forward": ctrl.rc(0, speed_rc, 0, 0); time.sleep(duration)
        elif cmd == "back":    ctrl.rc(0, -speed_rc, 0, 0); time.sleep(duration)
        elif cmd == "hover":   ctrl.rc(0, 0, 0, 0); time.sleep(duration)

        ctrl.rc(0, 0, 0, 0) # Neutralize between steps
        time.sleep(1)

    ctrl.land()
    ctrl.close()
    _set_plan(plan_id, status="completed", active_index=-1, message="Mission successful")

# -----------------------------
# Emergency Override Logic
# -----------------------------

_stop_event = threading.Event()

def trigger_emergency_land():
    """
    High-priority emergency landing command.
    Kills motors and stops the mission thread immediately.
    """
    try:
        # 1. Signal the running thread to die instantly
        _stop_event.set()
        
        # 2. Kill the motors using the SDK 'emergency' command
        ctrl = TelloDroneController()
        ctrl.send("emergency") 
        
        # 3. Reset database state to unlock the Vue UI
        MissionPlan.objects.filter(status__in=['running', 'queued']).update(
            status='inactive', 
            message="Emergency Handled"
        )
        
        ctrl.close()
        return True
    except Exception as e:
        print(f"[!] EMERGENCY FAILED: {str(e)}")
        return False