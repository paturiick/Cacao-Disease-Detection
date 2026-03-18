# drone_controller/live.py
import cv2
import threading
import time
import os
from .config import LOCAL_VIDEO_PORT

# CRITICAL FIX: Added fflags and flags to force low-latency decoding and drop broken packets.
# This prevents the 30-second OpenCV timeout and stops Daphne from hanging.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "protocol_whitelist;file,rtp,udp|fflags;nobuffer|flags;low_delay"

class VideoReceiver:
    def __init__(self, port: int = LOCAL_VIDEO_PORT):
        self.port = port
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_frame = b""
        
        # Initialize current_detections here so the _run thread 
        # doesn't crash if it starts before the first AI update.
        self.current_detections = [] 
        
        self.cap = None
        self.thread = None
        self.current_session_id = None

    def start(self):
        """Starts the background decoding thread instantly without blocking."""
        if self.thread and self.thread.is_alive():
            return  # Already running
            
        self._stop.clear()
        
        # The actual VideoCapture initialization is moved inside _run so this returns instantly
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"[VIDEO] Thread started. Attempting to connect on port {self.port} in the background...")

    def stop(self):
        """Kills the thread and cleans up memory."""
        print("[VIDEO] Stopping stream...")
        self._stop.set()
        
        # Safely shut down the thread
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
        # Clear the old frame and detections from memory
        with self._lock:
            self._last_frame = b""
            self.current_detections = []

    def update_detections(self, detections: list):
        """Called by the AI thread to update what we should draw."""
        with self._lock:
            self.current_detections = detections

    def _run(self):
        """Main loop that connects to the stream, captures frames, paints AI boxes, and encodes to JPEG."""
        
        # Connect to OpenCV in the background thread
        video_url = f"udp://@0.0.0.0:{self.port}?reuse=1"
        self.cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
        
        if not self.cap.isOpened():
            print(f"[VIDEO] Error: Could not open stream on {video_url}")
            return
            
        print("[VIDEO] Successfully connected to drone stream!")

        try:
            while not self._stop.is_set():
                if not self.cap or not self.cap.isOpened():
                    break
                    
                success, frame = self.cap.read()
                if success:
                    # --- PAINTING LAYER ---
                    with self._lock:
                        # Iterates through detections provided by the inference loop
                        for det in self.current_detections:
                            try:
                                # FIX: Cast coordinates to integers to prevent OpenCV TypeError
                                x1, y1, x2, y2 = map(int, det['box'])
                                label = det['label']
                                
                                # Check 'unhealthy' first because the string 'healthy' is in 'unhealthy'
                                # Red for diseased, Green for healthy
                                color = (0, 0, 255) if "unhealthy" in label.lower() else (0, 255, 0)
                                
                                # Draw the Bounding Box
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                # Draw the Label
                                cv2.putText(frame, label, (x1, y1 - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            except (KeyError, TypeError, ValueError):
                                # Skip malformed detections
                                continue

                    # Compress the annotated frame into a standard JPEG image
                    ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    if ret:
                        with self._lock:
                            # Store the actual bytes for the MJPEG stream to work in views.py
                            self._last_frame = buffer.tobytes()
                else:
                    # If we drop a frame, wait a tiny bit to prevent CPU spiking
                    time.sleep(0.01)
        finally:
            # FIX: Thread-safe cleanup. The thread releases the camera itself before dying.
            if self.cap:
                self.cap.release()
                self.cap = None
            print("[VIDEO] Port freed successfully.")

    def get_latest_frame(self) -> bytes:
        """
        Returns the actual JPEG bytes for the video feed.
        Used by the asynchronous generator in views.py.
        """
        with self._lock:
            return self._last_frame if self._last_frame else b""

    def get_latest_frame_size(self) -> int:
        """
        Returns the size of the latest frame.
        Used by the status dashboard health check.
        """
        with self._lock:
            return len(self._last_frame) if self._last_frame else 0