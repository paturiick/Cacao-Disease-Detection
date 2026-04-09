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
MODEL_PATH = "/app/models/ver6.pt" 
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.getcwd(), "models", "ver6.pt")

model = YOLO(MODEL_PATH)

def start_inference_loop():
    receiver = get_video_receiver()

    def loop():
        print(f"[AI] Starting YOLOv11 Inference with BoT-SORT...", flush=True)
        last_db_save_time = time.time()
        SAVE_INTERVAL_SECONDS = 3.0 
        
        active_session = None
        
        seen_pods = {} 
        
        # Dictionary for UI smoothing (prevents flickering)
        tracker_memory = {} 
        MEMORY_TIMEOUT = 0.15 # Seconds to keep a box alive on screen if detection drops

        while True:
            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                time.sleep(0.1)
                continue

            current_session = receiver.current_session_id
            if current_session != active_session:
                print(f"[AI] New session detected: {current_session}. Wiping memory.")
                active_session = current_session
                seen_pods.clear()
                tracker_memory.clear()

            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                continue

            try:
                results = model.track(
                    source=img, 
                    persist=True, 
                    tracker="/app/models/botsort.yaml", 
                    conf=0.4, 
                    iou=0.5,
                    verbose=False 
                )
                
                current_time = time.time()

                # Process current frame detections
                for result in results:
                    if result.boxes.id is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        track_ids = result.boxes.id.int().cpu().numpy()
                        clss = result.boxes.cls.int().cpu().numpy()
                        confs = result.boxes.conf.cpu().numpy()

                        for box, track_id, cls, conf in zip(boxes, track_ids, clss, confs):
                            label_name = model.names[cls].lower()

                            current_status = seen_pods.get(track_id, None)

                            # 1. Update the Database Dictionary
                            if "unhealthy" in label_name:
                                seen_pods[track_id] = "unhealthy"
                            elif "healthy" in label_name and current_status != "unhealthy":
                                seen_pods[track_id] = "healthy"

                            # 2. Update the UI Memory Dictionary
                            tracker_memory[track_id] = {
                                "box": list(map(int, box)), # Use list to ensure it's serializable
                                "label": f"ID:{track_id} {label_name} ({int(conf*100)}%)",
                                "last_seen": current_time
                            }

                # Build the list of boxes to send to the frontend
                new_detections = []
                active_ids = list(tracker_memory.keys())
                
                for tid in active_ids:
                    # If we haven't seen this ID for 0.5 seconds, remove it from UI memory
                    if current_time - tracker_memory[tid]["last_seen"] > MEMORY_TIMEOUT:
                        del tracker_memory[tid]
                    else:
                        # Otherwise, add it to the current frame's drawing list
                        new_detections.append({
                            "box": tracker_memory[tid]["box"],
                            "label": tracker_memory[tid]["label"]
                        })

                # Send smoothed boxes back to the video stream for the frontend
                receiver.update_detections(new_detections)

                # --- Database Saving Logic ---
                if active_session and (current_time - last_db_save_time) > SAVE_INTERVAL_SECONDS:
                    if len(seen_pods) > 0:
                        close_old_connections()
                        
                        healthy_count = sum(1 for status in seen_pods.values() if status == "healthy")
                        unhealthy_count = sum(1 for status in seen_pods.values() if status == "unhealthy")

                        session_log, _ = CacaoDetectionLog.objects.update_or_create(
                            session_id=active_session,
                            defaults={
                                'healthy_count': healthy_count,
                                'unhealthy_count': unhealthy_count
                            }
                        )

                        for pod_id, status in seen_pods.items():
                            DetectedCacao.objects.update_or_create(
                                session=session_log,
                                track_id=pod_id,
                                defaults={'status': status}
                            )

                    last_db_save_time = current_time

            except Exception as e:
                print(f"[AI] Inference Error: {e}")
            
            time.sleep(0.05) 

    threading.Thread(target=loop, daemon=True).start()