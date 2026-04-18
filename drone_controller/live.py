# drone_controller/live.py
import cv2
import threading
import time
import os
import uuid
from .config import LOCAL_VIDEO_PORT

# Force low-latency decoding and drop broken packets to prevent OpenCV hanging
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "protocol_whitelist;file,rtp,udp|fflags;nobuffer|flags;low_delay|timeout;2000000"
class VideoReceiver:
    def __init__(self, port: int = LOCAL_VIDEO_PORT):
        self.port = port
        self._lock = threading.Lock()
        self._last_frame = b""
        self.current_detections = [] 
        
        self.thread = None
        self._current_stop_event = None 

        #ids
        self.current_session_id = None
        self.current_plan_id = None

        self.is_recording = False
        self.video_writer = None
        self.recordings_dir = os.path.join(os.path.dirname(__file__), "recordings")
        os.makedirs(self.recordings_dir, exist_ok=True)
    
    def start_recording(self):
        with self._lock:
            if not self.is_recording:
                self.is_recording = True
                self.video_writer = None # Will be initialized by the thread on the next frame
                print("[VIDEO] Recording scheduled to start.")

    def stop_recording(self):
        with self._lock:
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
                print("[VIDEO] Recording saved successfully.")

    def start(self):
        """Starts the background decoding thread instantly without blocking."""
        if self.thread and self.thread.is_alive():
            return  
        
        self.current_session_id = str(uuid.uuid4())
            
        # Create a brand new kill switch strictly for THIS specific thread
        self._current_stop_event = threading.Event()
        
        # Pass the event directly into the thread so it owns its own state
        self.thread = threading.Thread(target=self._run, args=(self._current_stop_event,), daemon=True)
        self.thread.start()
        print(f"[VIDEO] Thread started. Attempting to connect on port {self.port}...")

    def stop(self):
        """Kills the thread and cleans up memory."""
        print("[VIDEO] Stopping stream...")
        
        # Trigger the kill switch for the currently active thread
        if self._current_stop_event:
            self._current_stop_event.set()
            
        # Safely wait for the thread to wrap up
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
        # Clear the old frame and detections from memory
        with self._lock:
            self._last_frame = b""
            self.current_detections = []
            self.current_session_id = None

    def update_detections(self, detections: list):
        """Called by the AI thread to update what we should draw."""
        with self._lock:
            self.current_detections = detections

    def _run(self, stop_event):
        """Main loop isolated to its own capture object and stop event."""
        video_url = f"udp://0.0.0.0:{self.port}"
        
        # --- THE FIX: Retry loop for OpenCV to wait for the drone ---
        cap = None
        print("[VIDEO] Waiting for drone stream to spin up...")
        for attempt in range(10): # Try for up to 5 seconds
            if stop_event.is_set():
                return
            cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
            if cap.isOpened():
                break
            print(f"[VIDEO] Stream not ready yet. Retrying... ({attempt+1}/10)")
            time.sleep(0.5)

        if not cap or not cap.isOpened():
            print(f"[VIDEO] Error: Could not open stream on {video_url} after retries.")
            return
            
        print("[VIDEO] Successfully connected to drone stream!")

        try:
            # Check this specific thread's stop event
            while not stop_event.is_set():
                success, frame = cap.read()
                if success:
                    with self._lock:
                        for det in self.current_detections:
                            try:
                                x1, y1, x2, y2 = map(int, det['box'])
                                label = det['label']
                                color = (0, 0, 255) if "unhealthy" in label.lower() else (0, 255, 0)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                cv2.putText(frame, label, (x1, y1 - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            except (KeyError, TypeError, ValueError):
                                continue

                        if self.is_recording:
                            if self.video_writer is None:
                                height, width = frame.shape[:2]
                                date_str = time.strftime("%Y-%m-%d_%H-%M-%S")
                                filename = os.path.join(self.recordings_dir, f"flight_{date_str}.mp4")

                                fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                                self.video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))
                            
                            self.video_writer.write(frame)

                    ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    if ret:
                        with self._lock:
                            self._last_frame = buffer.tobytes()
                else:
                    time.sleep(0.01)
        finally:
            if self.video_writer:
                self.video_writer.release()
            cap.release()
            print("[VIDEO] Port freed successfully.")

    def get_latest_frame(self) -> bytes:
        with self._lock:
            return self._last_frame if self._last_frame else b""

    def get_latest_frame_size(self) -> int:
        with self._lock:
            return len(self._last_frame) if self._last_frame else 0