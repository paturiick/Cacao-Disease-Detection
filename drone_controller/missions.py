from dataclasses import dataclass
from typing import List, Optional
import time
from .client import TelloClient

@dataclass
class MissionStep:
    cmd: str
    delay_s: float = 1.0

class MissionBuilder:

    def __init__(self):
        self.steps: List[MissionStep] = []

    def takeoff(self, delay_s: float = 2.0):
        self.steps.append(MissionStep("takeoff", delay_s))
        return self

    def land(self, delay_s: float = 1.0):
        self.steps.append(MissionStep("land", delay_s))
        return self

    def forward_cm(self, cm: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"forward {cm}", delay_s))
        return self

    def back_cm(self, cm: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"back {cm}", delay_s))
        return self

    def left_cm(self, cm: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"left {cm}", delay_s))
        return self

    def right_cm(self, cm: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"right {cm}", delay_s))
        return self

    def up_cm(self, cm: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"up {cm}", delay_s))
        return self

    def down_cm(self, cm: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"down {cm}", delay_s))
        return self

    def cw_deg(self, deg: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"cw {deg}", delay_s))
        return self

    def ccw_deg(self, deg: int, delay_s: float = 1.0):
        self.steps.append(MissionStep(f"ccw {deg}", delay_s))
        return self

class MissionExecutor:
    def __init__(self, client: TelloClient):
        self.client = client

    def run(self, steps: List[MissionStep], ensure_stream: bool = False) -> list[dict]:
        results = []
        self.client.connect()

        if ensure_stream:
            results.append(self._do("streamon", 0.2))

        for s in steps:
            results.append(self._do(s.cmd, s.delay_s))

        return results

    def _do(self, cmd: str, delay_s: float) -> dict:
        r = self.client.send(cmd)
        time.sleep(max(0.0, delay_s))
        return {"cmd": cmd, "ok": r.ok, "res": r.text, "ms": r.ms}