import socket
import threading
import time

class DroneService:
    def __init__(self):
        self.tello_address = ("192.168.10.1", 8889)
        self.local_port = 9001
        
        # Command Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.local_port))
        self.sock.settimeout(5.0)
        
        self.is_streaming = False

    def send_command(self, cmd):
        """Standard sender for drone instructions."""
        print(f"Executing: {cmd}")
        self.sock.sendto(cmd.encode(), self.tello_address)
        try:
            data, _ = self.sock.recvfrom(1024)
            return data.decode().strip()
        except socket.timeout:
            return "TIMEOUT"

    def initialize_drone(self):
        """Put drone in SDK mode and start video."""
        self.send_command("command")
        self.send_command("streamon")
        self.is_streaming = True

    def execute_mission(self, steps):
        """Loop through the steps from your Vue Mission Planner."""
        self.send_command("takeoff")
        for step in steps:
            # Example step: {'type': 'forward', 'val': 30}
            cmd = f"{step['type']} {step['val']}"
            self.send_command(cmd)
            time.sleep(1) # Safety delay
        self.send_command("land")

# Create a global instance
drone_manager = DroneService()