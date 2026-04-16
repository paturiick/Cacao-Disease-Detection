# drone_controller/live.py
import cv2
import threading
import time
import os
import uuid
import queue
from .config import LOCAL_VIDEO_PORT

# Force low-latency decoding and drop broken packets to prevent OpenCV hanging
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "protocol_whitelist;file,rtp,udp|fflags;nobuffer|flags;low_delay"

class VideoReceiver:
    def __init__(self, port: int = LOCAL_VIDEO_PORT):
        self.port = port
        self._lock = threading.Lock()
        self._last_frame = b""
        self.current_detections = [] 
        
        self.grabber_thread = None
        self.worker_thread = None
        self._current_stop_event = None 

        # Keep the queue very small (5 frames). 
        # If the worker thread falls behind, we WANT to drop old frames to maintain 0 latency.
        self.frame_queue = queue.Queue(maxsize=5)

        # ids
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
                self.video_writer = None # Will be initialized by the worker thread on the next frame
                print("[VIDEO] Recording scheduled to start.")

    def stop_recording(self):
        with self._lock:
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
                print("[VIDEO] Recording saved successfully.")

    def start(self):
        """Starts the background decoding and worker threads instantly."""
        if self.grabber_thread and self.grabber_thread.is_alive():
            return  
        
        self.current_session_id = str(uuid.uuid4())
            
        # Create a brand new kill switch strictly for this session
        self._current_stop_event = threading.Event()
        
        # Empty any stale frames from previous sessions
        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()

        # Spawn TWO threads: One to grab, one to process
        self.grabber_thread = threading.Thread(target=self._grabber_loop, args=(self._current_stop_event,), daemon=True)
        self.worker_thread = threading.Thread(target=self._worker_loop, args=(self._current_stop_event,), daemon=True)
        
        self.grabber_thread.start()
        self.worker_thread.start()
        
        print(f"[VIDEO] Threads started. Attempting to connect on port {self.port}...")

    def stop(self):
        """Kills the threads and cleans up memory."""
        print("[VIDEO] Stopping stream...")

        self.stop_recording()
        
        # Trigger the kill switch for the currently active threads
        if self._current_stop_event:
            self._current_stop_event.set()
            
        # Safely wait for both threads to wrap up
        if self.grabber_thread:
            self.grabber_thread.join(timeout=2.0)
            self.grabber_thread = None
            
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
            self.worker_thread = None
            
        # Clear the old frame and detections from memory
        with self._lock:
            self._last_frame = b""
            self.current_detections = []
            self.current_session_id = None

    def update_detections(self, detections: list):
        """Called by the AI thread to update what we should draw."""
        with self._lock:
            self.current_detections = detections

    # ==========================================
    # THREAD 1: THE GRABBER (Speed is everything)
    # ==========================================
    def _grabber_loop(self, stop_event):
        """Does NOTHING except pull frames from the UDP pipe to keep the OS buffer empty."""
        video_url = f"udp://@0.0.0.0:{self.port}"
        cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            print(f"[VIDEO] Error: Could not open stream on {video_url}")
            return
            
        print("[VIDEO] Successfully connected to drone stream!")

        try:
            while not stop_event.is_set():
                success, frame = cap.read()
                if success:
                    # If our worker thread is too slow and the queue is full, 
                    # violently throw away the oldest frame to make room for the new one.
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    
                    # Shove the raw frame into the queue
                    self.frame_queue.put(frame)
                else:
                    time.sleep(0.01)
        finally:
            cap.release()
            print("[VIDEO] UDP Port freed successfully.")

    # ==========================================
    # THREAD 2: THE WORKER (Heavy Lifting)
    # ==========================================
    def _worker_loop(self, stop_event):
        """Pulls frames from the queue and handles bounding boxes, MP4 saving, and JPEG encoding."""
        try:
            while not stop_event.is_set():
                try:
                    # Wait up to 0.1s for a frame to arrive
                    frame = self.frame_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # 1. DRAW BOUNDING BOXES
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

                    # 2. SAVE TO MP4 FILE
                    if self.is_recording:
                        if self.video_writer is None:
                            height, width = frame.shape[:2]
                            date_str = time.strftime("%Y-%m-%d_%H-%M-%S")
                            filename = os.path.join(self.recordings_dir, f"flight_{date_str}.mp4")

                            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                            self.video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))
                        
                        self.video_writer.write(frame)

                # 3. ENCODE TO JPEG FOR THE WEB DASHBOARD
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    with self._lock:
                        self._last_frame = buffer.tobytes()
                        
        finally:
            # Safely release this thread's specific capture object before dying
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

    def get_latest_frame(self) -> bytes:
        with self._lock:
            return self._last_frame if self._last_frame else b""

    def get_latest_frame_size(self) -> int:
        with self._lock:
            return len(self._last_frame) if self._last_frame else 0