import socket
import threading
from .config import LOCAL_VIDEO_PORT

class VideoReceiver:
    def __init__(self, port: int = LOCAL_VIDEO_PORT):
        self.port = port
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_packet = b""

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.sock.settimeout(1.0)

        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            try:
                pkt, _ = self.sock.recvfrom(4096) 
            except socket.timeout:
                continue
            with self._lock:
                self._last_packet = pkt

    def get_latest_packet(self) -> bytes:
        """Returns the raw h264 packet for the backend to decode."""
        with self._lock:
            return self._last_packet
            
    def last_packet_size(self) -> int:
        with self._lock:
            return len(self._last_packet)