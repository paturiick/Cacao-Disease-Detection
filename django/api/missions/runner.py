# api/missions/runner.py
import threading
import time
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from .models import MissionPlan, MissionStep

# -----------------------------
# Fake Drone Controller (TEST)
# -----------------------------
@dataclass
class DroneResult:
    ok: bool
    message: str = ""

class FakeDroneController:
    """
    Fake controller used to validate:
    Frontend -> Backend -> Runner -> "Drone" execution

    No Wi-Fi, no real drone required.
    Prints commands to Django console and returns ok.
    """

    def __init__(self, simulate_latency_s: float = 0.05):
        self.simulate_latency_s = simulate_latency_s
        self.connected = False

    def _latency(self):
        time.sleep(self.simulate_latency_s)

    def connect(self) -> DroneResult:
        self._latency()
        self.connected = True
        print("[FAKE-DRONE] connect() -> ok")
        return DroneResult(True, "connected")

    def enter_sdk(self) -> DroneResult:
        self._latency()
        print("[FAKE-DRONE] enter_sdk(command) -> ok")
        return DroneResult(True, "ok")

    def takeoff(self) -> DroneResult:
        self._latency()
        print("[FAKE-DRONE] takeoff() -> ok")
        return DroneResult(True, "ok")

    def land(self) -> DroneResult:
        self._latency()
        print("[FAKE-DRONE] land() -> ok")
        return DroneResult(True, "ok")

    def rc(self, roll: int, pitch: int, throttle: int, yaw: int) -> DroneResult:
        self._latency()
        print(f"[FAKE-DRONE] rc({roll},{pitch},{throttle},{yaw}) -> ok")
        return DroneResult(True, "ok")

    def stop(self) -> DroneResult:
        self._latency()
        print("[FAKE-DRONE] stop() -> ok")
        return DroneResult(True, "ok")

    def disconnect(self) -> DroneResult:
        self._latency()
        self.connected = False
        print("[FAKE-DRONE] disconnect() -> ok")
        return DroneResult(True, "disconnected")


# -----------------------------
# Runner State (simple)
# -----------------------------
_running_lock = threading.Lock()
_running_threads = {}  # plan_id -> thread


def _speed_to_rc(speed_m_s: float) -> int:
    """
    Simple mapping for test:
      1.0 m/s -> 20
      3.0 m/s -> 60
      5.0 m/s -> 100 (cap)
    """
    try:
        v = float(speed_m_s)
    except Exception:
        v = 1.0
    rc = int(v * 20)
    return max(10, min(100, rc))


def start_plan(plan_id: int) -> bool:
    """
    Called by your /run endpoint.
    Starts a background thread if not already running.
    """
    with _running_lock:
        t = _running_threads.get(plan_id)
        if t and t.is_alive():
            return False

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
    ctrl = FakeDroneController()

    # --- mark queued ---
    _set_plan(plan_id, status="queued", message="Queued", active_index=-1)

    # --- "connect" + takeoff (fake) ---
    ctrl.connect()
    ctrl.enter_sdk()

    takeoff = ctrl.takeoff()
    if not takeoff.ok:
        _set_plan(plan_id, status="failed", message=f"Takeoff failed: {takeoff.message}", active_index=-1)
        ctrl.disconnect()
        return

    # --- init config (backend active_index = 0) ---
    plan = MissionPlan.objects.get(id=plan_id)
    speed_rc = _speed_to_rc(plan.speed)

    _set_plan(
        plan_id,
        status="running",
        active_index=0,
        gps="Strong",
        battery=84,
        message="Initial configuration",
        updated_at=timezone.now() if hasattr(MissionPlan, "updated_at") else None,
    )
    time.sleep(1.0)

    steps = list(MissionStep.objects.filter(plan_id=plan_id).order_by("order", "id"))

    # --- execute steps (backend active_index = 1..n) ---
    for i, step in enumerate(steps, start=1):
        # allow cancel from DB
        plan = MissionPlan.objects.get(id=plan_id)
        if plan.status == "cancelled":
            _set_plan(plan_id, active_index=-1, message="Cancelled")
            ctrl.land()
            ctrl.disconnect()
            return

        duration = max(0.1, float(step.val))

        _set_plan(
            plan_id,
            active_index=i,
            message=f"Executing {step.type} for {duration:.1f}s",
            gps="Strong",
            battery=84,
        )

        # map command type -> rc axes (fake)
        if step.type == "hover":
            ctrl.stop()
            time.sleep(duration)
            continue

        if step.type == "up":
            ctrl.rc(0, 0, +speed_rc, 0)
        elif step.type == "down":
            ctrl.rc(0, 0, -speed_rc, 0)
        elif step.type == "left":
            ctrl.rc(-speed_rc, 0, 0, 0)
        elif step.type == "right":
            ctrl.rc(+speed_rc, 0, 0, 0)
        elif step.type == "forward":
            ctrl.rc(0, +speed_rc, 0, 0)
        elif step.type == "back":
            ctrl.rc(0, -speed_rc, 0, 0)
        elif step.type == "cw":
            ctrl.rc(0, 0, 0, +speed_rc)
        elif step.type == "ccw":
            ctrl.rc(0, 0, 0, -speed_rc)
        else:
            # invalid / unknown
            _set_plan(plan_id, status="failed", message=f"Invalid step type: {step.type}", active_index=-1)
            ctrl.land()
            ctrl.disconnect()
            return

        time.sleep(duration)
        ctrl.stop()

    # --- finish ---
    ctrl.land()
    ctrl.disconnect()

    _set_plan(plan_id, status="completed", active_index=-1, message="Mission completed")