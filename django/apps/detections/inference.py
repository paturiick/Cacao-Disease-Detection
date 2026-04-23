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

TRACKER_PATH = "/app/models/botsort.yaml"
if not os.path.exists(TRACKER_PATH):
    TRACKER_PATH = os.path.join(os.getcwd(), "models", "botsort.yaml")

# ------------------------------------------
# Inference configuration
# ------------------------------------------
INFER_SIZE = (640, 640)   # match new-code.txt reference
CONF_THRESH = 0.7         # match new-code.txt reference
IOU_THRESH = 0.8          # match new-code.txt reference
LOOP_SLEEP_SECONDS = 0.5
SAVE_INTERVAL_SECONDS = 3.0

# ===================================asd=======
# 1. VERIFY GPU AND LOAD MODEL
# ==========================================
has_gpu = torch.cuda.is_available()
print(f"\n[AI SYSTEM] CUDA GPU Available: {has_gpu}")
if has_gpu:
    print(f"[AI SYSTEM] Using GPU: {torch.cuda.get_device_name(0)}")

target_device = 0 if has_gpu else "cpu"
model = YOLO(MODEL_PATH)

# ==========================================
# 2. WARM UP THE GPU
# ==========================================
# PyTorch spikes memory massively on its first prediction.
# We run a dummy frame now so it doesn't crash the server later when the stream starts.
try:
    print("[AI SYSTEM] Warming up GPU (This might take a few seconds)...")
    dummy_frame = np.zeros((INFER_SIZE[1], INFER_SIZE[0], 3), dtype=np.uint8)
    model.predict(source=dummy_frame, device=target_device, verbose=False)
    print("[AI SYSTEM] Warmup Complete. AI is ready to track.\n")
except Exception as e:
    print(f"[AI SYSTEM] Warning: Warmup failed: {e}")


def capture_and_save_detection(frame, track_id, status, session_id, mission_id):
    """Triggered exactly once per pod to grab the frame and GPS instantly."""
    try:
        live_state = LiveSystemState.objects.first()
        if live_state:
            lat, lon = getattr(live_state, 'gps_lat', None), getattr(live_state, 'gps_lon', None)
            yaw = getattr(live_state, 'yaw', None)
            roll = getattr(live_state, 'roll', None)
            pitch = getattr(live_state, 'pitch', None)
        else:
            lat, lon, yaw, roll, pitch = None, None, None, None, None
    except Exception as e:
        print(f"[AI] Telemetry fetch error: {e}")
        lat, lon, yaw, roll, pitch = None, None, None, None, None

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
            'yaw': yaw,
            'roll': roll,
            'pitch': pitch
        }
    )


def _scale_box_from_normalized(box_n, width, height):
    """Convert normalized xyxy to original frame pixel coordinates."""
    x1n, y1n, x2n, y2n = box_n

    x1 = int(x1n * width)
    y1 = int(y1n * height)
    x2 = int(x2n * width)
    y2 = int(y2n * height)

    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))

    return [x1, y1, x2, y2]


def start_inference_loop():
    receiver = get_video_receiver()

    def loop():
        last_db_save_time = time.time()

        active_session = None
        seen_pods = {}
        captured_ids = set()

        while True:
            # Sleep prevents the loop from consuming 100% CPU when no stream is active
            time.sleep(LOOP_SLEEP_SECONDS)

            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                time.sleep(LOOP_SLEEP_SECONDS)
                continue

            current_session = receiver.current_session_id
            current_plan = getattr(receiver, 'current_plan_id', None)

            if current_session != active_session:
                active_session = current_session
                seen_pods.clear()
                captured_ids.clear()

            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            try:
                orig_h, orig_w = img.shape[:2]
                annotated_frame = img.copy()

                # Match new-code.txt behavior:
                # 1) force exact 640x640 preprocessing
                # 2) run tracking on resized frame
                # 3) map detections back to original-size output frame
                frame_640 = cv2.resize(img, INFER_SIZE, interpolation=cv2.INTER_LINEAR)

                results = model.track(
                    source=frame_640,
                    persist=True,
                    tracker=TRACKER_PATH,
                    conf=CONF_THRESH,
                    iou=IOU_THRESH,
                    verbose=False,
                    device=target_device,
                )

                new_detections = []
                r = results[0] if results else None

                if r is not None and r.boxes is not None and len(r.boxes) > 0:
                    boxes = r.boxes
                    xyxyn = boxes.xyxyn.cpu().numpy()
                    confs = boxes.conf.cpu().numpy()
                    clss = boxes.cls.cpu().numpy().astype(int)

                    if boxes.id is not None:
                        track_ids = boxes.id.int().cpu().numpy()
                    else:
                        track_ids = np.full(len(xyxyn), -1, dtype=int)

                    for box_n, track_id, cls, conf in zip(xyxyn, track_ids, clss, confs):
                        label_name = model.names[cls].lower()
                        status = "unhealthy" if "unhealthy" in label_name else "healthy"
                        x1, y1, x2, y2 = _scale_box_from_normalized(box_n, orig_w, orig_h)

                        color = (0, 0, 255) if status == "unhealthy" else (0, 255, 0)
                        label_text = f"ID:{track_id} {label_name} ({int(conf * 100)}%)" if track_id != -1 else f"{label_name} ({int(conf * 100)}%)"

                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(
                            annotated_frame,
                            label_text,
                            (x1, max(20, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            color,
                            2,
                        )

                        if track_id != -1:
                            seen_pods[track_id] = status

                            if current_plan and active_session and (track_id not in captured_ids):
                                capture_and_save_detection(
                                    annotated_frame,
                                    track_id,
                                    status,
                                    active_session,
                                    current_plan,
                                )
                                captured_ids.add(track_id)

                        new_detections.append({
                            "box": [x1, y1, x2, y2],
                            "label": label_text,
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
                            defaults={
                                'flight_plan_id': current_plan,
                                'healthy_count': h_count,
                                'unhealthy_count': u_count,
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
                print(f"[AI] Tracking Error: {e}")

    threading.Thread(target=loop, daemon=True).start()
