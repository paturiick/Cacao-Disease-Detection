# apps/detections/inference.py
import os
import threading
import time
import cv2
import numpy as np
from django.db import close_old_connections
from ultralytics import YOLO
from drone_controller.instance import get_video_receiver
from .models import CacaoDetectionLog, DetectedCacao

# Load your custom YOLOv11 model
# Defaulting to the path typically used in your Docker/Linux environment
MODEL_PATH = "/app/models/ver6.pt" 
if not os.path.exists(MODEL_PATH):
    # Fallback to local directory for development
    MODEL_PATH = os.path.join(os.getcwd(), "models", "ver6.pt")

model = YOLO(MODEL_PATH)

def start_inference_loop():
    """
    Launches the background AI thread. 
    This is called once by apps.py when Django starts.
    """
    receiver = get_video_receiver()

    def loop():
        print(f"[AI] Starting YOLOv11 Inference with BoT-SORT...", flush=True)
        last_db_save_time = time.time()
        SAVE_INTERVAL_SECONDS = 3.0 
        
        active_session = None
        # Use a dictionary to map track_id -> status to prevent double-counting
        seen_pods = {} 

        while True:
            # 1. Fetch the raw frame from the Drone Controller's VideoReceiver
            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                time.sleep(0.1)
                continue

            # 2. Track Session and Mission state
            current_session = receiver.current_session_id
            current_plan = getattr(receiver, 'current_plan_id', None) # Linked to FlightPlan ID

            # If the session changes (new flight), clear local memory
            if current_session != active_session:
                print(f"[AI] New session detected: {current_session}. Wiping memory.")
                active_session = current_session
                seen_pods.clear()

            # 3. Decode frame for OpenCV/YOLO
            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                continue

            try:
                # 4. Run YOLOv11 Tracking
                # persist=True is required to maintain IDs across individual frames
                results = model.track(
                    source=img, 
                    persist=True, 
                    tracker="/app/models/botsort.yaml", # Ensure this file exists in your working directory
                    conf=0.7, 
                    iou=0.5,
                    verbose=False 
                )
                
                new_detections = []

                # 5. Process tracking results
                for result in results:
                    if result.boxes.id is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        track_ids = result.boxes.id.int().cpu().numpy()
                        clss = result.boxes.cls.int().cpu().numpy()
                        confs = result.boxes.conf.cpu().numpy()

                        for box, track_id, cls, conf in zip(boxes, track_ids, clss, confs):
                            label_name = model.names[cls].lower()

                            # Update dictionary: ensures a pod is only 'healthy' OR 'unhealthy'
                            if "unhealthy" in label_name:
                                seen_pods[track_id] = "unhealthy"
                            elif "healthy" in label_name:
                                seen_pods[track_id] = "healthy"

                            # Prepare data for the frontend video overlay
                            new_detections.append({
                                "box": [int(x) for x in box],
                                "label": f"ID:{track_id} {label_name} ({int(conf*100)}%)"
                            })

                # 6. Push boxes back to VideoReceiver for the Vue frontend to draw
                receiver.update_detections(new_detections)

                # 7. Database Saving Logic (The Gatekeeper)
                current_time = time.time()
                
                # We ONLY save if a FlightPlan (Mission) is active and the timer has elapsed
                if current_plan and active_session and (current_time - last_db_save_time) > SAVE_INTERVAL_SECONDS:
                    if len(seen_pods) > 0:
                        # Prevent "Database gone away" errors in daemon threads
                        close_old_connections()
                        
                        healthy_count = sum(1 for status in seen_pods.values() if status == "healthy")
                        unhealthy_count = sum(1 for status in seen_pods.values() if status == "unhealthy")

                        # Save/Update the summary log
                        session_log, _ = CacaoDetectionLog.objects.update_or_create(
                            session_id=active_session,
                            defaults={
                                'flight_plan_id': current_plan,
                                'healthy_count': healthy_count,
                                'unhealthy_count': unhealthy_count
                            }
                        )

                        # Save/Update individual pod records
                        for pod_id, status in seen_pods.items():
                            DetectedCacao.objects.update_or_create(
                                session=session_log,
                                track_id=pod_id,
                                defaults={'status': status}
                            )

                    last_db_save_time = current_time

            except Exception as e:
                print(f"[AI] Inference Error: {e}")
            
            # Control the loop frequency to save CPU
            time.sleep(0.01) 

    # Start the loop in a background thread so Django remains responsive
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()