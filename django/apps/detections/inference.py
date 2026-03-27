# apps/detections/inference.py
import os
import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO
from drone_controller.instance import get_video_receiver
from .models import CacaoDetectionLog, DetectedCacao

MODEL_PATH = "/app/models/ver5.pt"
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.getcwd(), "models", "ver5.pt")

model = YOLO(MODEL_PATH)

def start_inference_loop():
    receiver = get_video_receiver()

    def loop():
        print(f"[AI] Starting Inference with BoT-SORT tracking...", flush=True)
        last_db_save_time = time.time()
        SAVE_INTERVAL_SECONDS = 3.0 
        
        active_session = None
        seen_healthy_ids = set()
        seen_unhealthy_ids = set()

        while True:
            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                time.sleep(0.1)
                continue

            current_session = receiver.current_session_id
            if current_session != active_session:
                print(f"[AI] New session detected: {current_session}. Wiping memory.")
                active_session = current_session
                seen_healthy_ids.clear()
                seen_unhealthy_ids.clear()

            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                continue

            try:
                results = model.track(img, persist=True, tracker="/app/models/botsort.yaml", verbose=False, conf=0.25, device=0)
                
                new_detections = []

                for result in results:
                    if result.boxes.id is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        track_ids = result.boxes.id.int().cpu().numpy()
                        clss = result.boxes.cls.int().cpu().numpy()
                        confs = result.boxes.conf.cpu().numpy()

                        for box, track_id, cls, conf in zip(boxes, track_ids, clss, confs):
                            label_name = model.names[cls].lower()

                            if "unhealthy" in label_name:
                                seen_unhealthy_ids.add(track_id)
                            elif "healthy" in label_name:
                                seen_healthy_ids.add(track_id)

                            new_detections.append({
                                "box": map(int, box),
                                "label": f"ID:{track_id} {label_name} ({int(conf*100)}%)"
                            })

                receiver.update_detections(new_detections)

                current_time = time.time()
                if active_session and (current_time - last_db_save_time) > SAVE_INTERVAL_SECONDS:
                    if len(seen_healthy_ids) > 0 or len(seen_unhealthy_ids) > 0:
                        
                        # 1. Update main session log
                        session_log, _ = CacaoDetectionLog.objects.update_or_create(
                            session_id=active_session,
                            defaults={
                                'healthy_count': len(seen_healthy_ids),
                                'unhealthy_count': len(seen_unhealthy_ids)
                            }
                        )

                        # 2. Update healthy pods
                        for pod_id in seen_healthy_ids:
                            DetectedCacao.objects.update_or_create(
                                session=session_log,
                                track_id=pod_id,
                                defaults={'status': 'healthy'}
                            )

                        # 3. Update unhealthy pods
                        for pod_id in seen_unhealthy_ids:
                            DetectedCacao.objects.update_or_create(
                                session=session_log,
                                track_id=pod_id,
                                defaults={'status': 'unhealthy'}
                            )

                    last_db_save_time = current_time

            except Exception as e:
                print(f"[AI] Inference Error: {e}")
            
            time.sleep(0.05) 

    threading.Thread(target=loop, daemon=True).start()