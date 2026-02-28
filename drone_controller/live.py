import socket
import threading
from .config import LOCAL_VIDEO_PORT

class VideoReceiver:
    def __init__(self, port: int = LOCAL_VIDEO_PORT):
        self.port = port
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_packet = b""
        
        # Don't bind the socket or thread yet!
        self.sock = None
        self.thread = None

    def start(self):
        """Opens the port and starts the thread."""
        if self.thread and self.thread.is_alive():
            return  # Already running
            
        self._stop.clear()
        
        # 1. Open the socket only when the user clicks 'Start Stream'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.sock.settimeout(1.0)

        # 2. Create a fresh thread every time
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"[VIDEO] Stream started. Listening on port {self.port}")

    def stop(self):
        """Kills the thread and frees the port."""
        print("[VIDEO] Stopping stream...")
        self._stop.set()
        
        # 3. Explicitly close the socket so the port is freed for next time
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
            
        # Clear the old frame from memory
        with self._lock:
            self._last_packet = b""
            
        # Safely shut down the thread
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        print("[VIDEO] Port freed successfully.")

    def _run(self):
        while not self._stop.is_set():
            if not self.sock:
                break
                
            try:
                pkt, _ = self.sock.recvfrom(4096) 
                with self._lock:
                    self._last_packet = pkt
            except socket.timeout:
                continue
            except OSError:
                # This catches the error when self.sock.close() is called mid-loop
                break 

    def get_latest_packet(self) -> bytes:
        """Returns the raw h264 packet for the backend to decode."""
        with self._lock:
            return self._last_packet
            
    def last_packet_size(self) -> int:
        with self._lock:
            return len(self._last_packet)