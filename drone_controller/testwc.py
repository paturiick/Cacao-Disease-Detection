# apps/detections/inference.py
import os
import threading
import time
import cv2
import numpy as np
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
from drone_controller.instance import get_video_receiver

load_dotenv()

client = InferenceHTTPClient.init(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

def start_inference_loop():
    receiver = get_video_receiver()
    
    # Combined according to your SDK requirements
    # Format: "workspace_id/workflow_id"
    full_workflow_path = "cacao-i3ehv/wf1" 

    def loop():
        print(f"[AI] Starting Workflow Inference: {full_workflow_path}...")
        while True:
            frame_bytes = receiver.get_latest_frame()
            if not frame_bytes:
                time.sleep(0.5)
                continue

            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            try:
                # FIX: Removed 'workspace' argument and used the combined path
                result = client.infer_from_workflow(
                    workflow_id=full_workflow_path,
                    images={"image": img}
                )
                
                new_detections = []
                # Workflows return a dict with output names as keys
                # In your reference, the output is likely 'predictions' or the model step name
                output_data = result[0] if isinstance(result, list) else result
                
                # Check for common Roboflow workflow output keys
                predictions = output_data.get('predictions', []) 
                
                for pred in predictions:
                    x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
                    x1, y1 = int(x - w/2), int(y - h/2)
                    x2, y2 = int(x + w/2), int(y + h/2)
                    
                    new_detections.append({
                        "box": [x1, y1, x2, y2],
                        "label": f"{pred['class']} ({int(pred['confidence']*100)}%)"
                    })

                receiver.update_detections(new_detections)

            except Exception as e:
                print(f"[AI] Workflow Error: {e}")
            
            time.sleep(0.2)

    threading.Thread(target=loop, daemon=True).start()