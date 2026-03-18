# apps/detections/inference.py
import os
import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO
from drone_controller.instance import get_video_receiver
from .models import CacaoDetectionLog

MODEL_PATH = "/app/models/best.pt"
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.getcwd(), "models", "best.pt")

model = YOLO(MODEL_PATH)

def start_inference_loop():
    receiver = get_video_receiver()

    def loop():
        print(f"[AI] Starting Inference with: {MODEL_PATH}...")
        last_db_save_time = time.time()
        SAVE_INTERVAL_SECONDS = 3.0 

        while True:
            # 1. Grab the raw JPEG bytes from live.py
            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                time.sleep(0.1)
                continue

            # 2. Decode for the AI
            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                continue

            try:
                # 3. Run YOLO (No painting needed here!)
                results = model(img, verbose=False, conf=0.25, device=0)
                
                healthy_count = 0
                unhealthy_count = 0
                new_detections = []

                for result in results:
                    for box in result.boxes:
                        coords = box.xyxy[0].tolist()
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        label_name = model.names[cls].lower()

                        if "unhealthy" in label_name:
                            unhealthy_count += 1
                        elif "healthy" in label_name:
                            healthy_count += 1

                        new_detections.append({
                            "box": map(int, coords),
                            "label": f"{label_name} ({int(conf*100)}%)"
                        })

                # 4. Send the coordinates to live.py so IT can draw them
                receiver.update_detections(new_detections)

                # 5. Save stats to the database
                current_time = time.time()
                if (current_time - last_db_save_time) > SAVE_INTERVAL_SECONDS:
                    if healthy_count > 0 or unhealthy_count > 0:
                        CacaoDetectionLog.objects.create(
                            healthy_count=healthy_count,
                            unhealthy_count=unhealthy_count
                        )
                    last_db_save_time = current_time

            except Exception as e:
                print(f"[AI] Inference Error: {e}")
            
            time.sleep(0.05) 

    threading.Thread(target=loop, daemon=True).start()