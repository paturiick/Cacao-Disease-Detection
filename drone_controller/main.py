from .client import TelloClient
from .live import VideoReceiver
from .telemetry import TelemetryReceiver
from .missions import MissionExecutor, MissionBuilder

class DroneBrain:
    def __init__(self):
        self.client = TelloClient()
        self.telemetry = TelemetryReceiver()
        self.video = VideoReceiver()
        self.mission_executor = MissionExecutor(self.client)

    def connect_and_initialize(self) -> bool:
        """Connects to the drone and starts all background services."""
        print("Connecting to drone...")
        reply = self.client.connect()
        
        if reply.ok:
            print("Connected! Initializing subsystems...")
            # Start telemetry polling
            self.telemetry.start()
            
            # Enable video streaming on the drone and start local receiver
            self.client.send("streamon")
            self.video.start()
            return True
            
        print(f"Failed to connect: {reply.text}")
        return False

    def shutdown(self):
        """Safely stops streams and threads."""
        self.client.send("streamoff")
        self.telemetry.stop()
        self.video.stop()
        self.client._connected = False
        print("Drone disconnected and background threads stopped.")

    def run_flight_plan(self, steps: list):
        """Passes a configured flight plan to the executor."""
        return self.mission_executor.run(steps, ensure_stream=False)

    def get_current_state(self) -> dict:
        """Exposes telemetry data for your backend."""
        return self.telemetry.get()

    def get_video_stream(self) -> bytes:
        """Exposes the latest video packet for backend consumption."""
        return self.video.get_latest_packet()

# Example usage for testing locally:
if __name__ == "__main__":
    import time
    
    brain = DroneBrain()
    if brain.connect_and_initialize():
        try:
            print("Fetching telemetry for 5 seconds...")
            for _ in range(5):
                state = brain.get_current_state()
                print(f"Battery: {state['battery']}%, Altitude: {state['alt_m']}m")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("Interrupted by user.")
        finally:
            brain.shutdown()