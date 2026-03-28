# drone_controller/instance.py
from .client import TelloClient
from .live import VideoReceiver
from .telemetry import TelemetryReceiver
from .missions import MissionExecutor

# Private variables to hold the singletons
_drone_client = None
_video_receiver = None
_telemetry_receiver = None
_mission_executor = None

def get_drone_client():
    global _drone_client
    if _drone_client is None:
        _drone_client = TelloClient()
    return _drone_client

def get_video_receiver():
    global _video_receiver
    if _video_receiver is None:
        _video_receiver = VideoReceiver()
    return _video_receiver

def get_telemetry_receiver():
    global _telemetry_receiver
    if _telemetry_receiver is None:
        _telemetry_receiver = TelemetryReceiver()
        _telemetry_receiver.start()
    return _telemetry_receiver

def get_mission_executor():
    global _mission_executor
    if _mission_executor is None:
        # The executor needs the client to send flight commands
        _mission_executor = MissionExecutor(get_drone_client())
    return _mission_executor