import os
import threading
import time
import cv2
import numpy as np
import torch

from django.conf import settings
from django.db import close_old_connections
from ultralytics import YOLO
from drone_controller.instance import get_video_receiver

# Import your Cacao and Telemetry models
from .models import CacaoDetectionLog, DetectedCacao
from apps.telemetry.models import LiveSystemState 

MODEL_PATH = "/app/models/ver6.pt" 
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.getcwd(), "models", "ver6.pt")

# ==========================================
# 1. VERIFY GPU AND LOAD MODEL
# ==========================================
has_gpu = torch.cuda.is_available()
print(f"\n[AI SYSTEM] CUDA GPU Available: {has_gpu}")
if has_gpu:
    print(f"[AI SYSTEM] Using GPU: {torch.cuda.get_device_name(0)}")

model = YOLO(MODEL_PATH)

# ==========================================
# 2. WARM UP THE GPU
# ==========================================
# PyTorch spikes memory massively on its first prediction.
# We run a dummy frame now so it doesn't crash the server later when the stream starts.
try:
    print("[AI SYSTEM] Warming up GPU (This might take a few seconds)...")
    dummy_frame = np.zeros((416, 416, 3), dtype=np.uint8)
    # Explicitly use device=0 if GPU is available, else fallback to cpu
    target_device = 0 if has_gpu else 'cpu' 
    model.predict(source=dummy_frame, device=target_device, verbose=False)
    print("[AI SYSTEM] Warmup Complete. AI is ready to track.\n")
except Exception as e:
    print(f"[AI SYSTEM] Warning: Warmup failed: {e}")


def capture_and_save_detection(frame, track_id, status, session_id, mission_id):
    """Triggered exactly once per pod to grab the frame and GPS instantly."""
    try:
        live_state = LiveSystemState.objects.get(id=1)
        lat, lon = live_state.gps_lat, live_state.gps_lon
    except LiveSystemState.DoesNotExist:
        lat, lon = None, None

    media_rel_path = f"detect/{session_id}"
    media_dir = os.path.join(settings.MEDIA_ROOT, media_rel_path)
    os.makedirs(media_dir, exist_ok=True)
    
    filename = f"pod_{track_id}_{status}.jpg"
    filepath = os.path.join(media_dir, filename)
    cv2.imwrite(filepath, frame)

    session_log, _ = CacaoDetectionLog.objects.get_or_create(
        session_id=session_id,
        defaults={'flight_plan_id': mission_id}
    )

    DetectedCacao.objects.update_or_create(
        session=session_log,
        track_id=track_id,
        defaults={
            'status': status,
            'image': f"{media_rel_path}/{filename}",
            'latitude': lat,
            'longitude': lon,
        }
    )


def start_inference_loop():
    receiver = get_video_receiver()

    def loop():
        last_db_save_time = time.time()
        SAVE_INTERVAL_SECONDS = 3.0 
        
        active_session = None
        seen_pods = {} 
        captured_ids = set()

        while True:
            # Sleep prevents the loop from consuming 100% CPU when no stream is active
            time.sleep(0.5) 

            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                continue

            current_session = receiver.current_session_id
            current_plan = getattr(receiver, 'current_plan_id', None)

            if current_session != active_session:
                active_session = current_session
                seen_pods.clear()
                captured_ids.clear()

            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None: continue

            try:
                # ==========================================
                # 3. FORCE GPU INFERENCE (device=0)
                # ==========================================
                # imgsz=416 cuts the VRAM requirement in half to prevent crashes
                results = model.track(
                    source=img, 
                    persist=True, 
                    tracker="/app/models/botsort.yaml", 
                    conf=0.5, 
                    iou=0.7, 
                    verbose=False, 
                    imgsz=640, 
                    device=0 if has_gpu else 'cpu' 
                )
                
                new_detections = []

                for result in results:
                    annotated_frame = img.copy()

                    if result.boxes.id is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        track_ids = result.boxes.id.int().cpu().numpy()
                        clss = result.boxes.cls.int().cpu().numpy()
                        confs = result.boxes.conf.cpu().numpy()

                        for box, track_id, cls, conf in zip(boxes, track_ids, clss, confs):
                            label_name = model.names[cls].lower()
                            status = "unhealthy" if "unhealthy" in label_name else "healthy"

                            color = (0, 0, 255) if status == "unhealthy" else (0, 255, 0)
                            x1, y1, x2, y2 = map(int, box)
                            label_text = f"ID:{track_id} {label_name} ({int(conf*100)}%)"

                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(annotated_frame, label_text, (x1, y1 - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        
                        for box, track_id, cls, conf in zip(boxes, track_ids, clss, confs):
                            label_name = model.names[cls].lower()
                            status = "unhealthy" if "unhealthy" in label_name else "healthy"

                            seen_pods[track_id] = status

                            if current_plan and active_session and (track_id not in captured_ids):
                                capture_and_save_detection(annotated_frame, track_id, status, active_session, current_plan)
                                captured_ids.add(track_id)

                            new_detections.append({
                                "box": [int(x) for x in box],
                                "label": f"ID:{track_id} {label_name} ({int(conf*100)}%)"
                            })

                receiver.update_detections(new_detections)

                current_time = time.time()
                if current_plan and active_session and (current_time - last_db_save_time) > SAVE_INTERVAL_SECONDS:
                    if len(seen_pods) > 0:
                        close_old_connections()
                        h_count = sum(1 for s in seen_pods.values() if s == "healthy")
                        u_count = sum(1 for s in seen_pods.values() if s == "unhealthy")

                        session_log, _ = CacaoDetectionLog.objects.update_or_create(
                            session_id=active_session,
                            defaults={'flight_plan_id': current_plan, 'healthy_count': h_count, 'unhealthy_count': u_count}
                        )
                        for pod_id, status in seen_pods.items():
                            DetectedCacao.objects.update_or_create(session=session_log, track_id=pod_id, defaults={'status': status})
                    last_db_save_time = current_time

            except Exception as e:
                print(f"[AI] Tracking Error: {e}")

    threading.Thread(target=loop, daemon=True).start()