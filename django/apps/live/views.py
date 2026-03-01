# apps/live/views.py
import json
import asyncio
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drone_controller.instance import get_video_receiver, get_drone_client

async def generate_frames():
    receiver = get_video_receiver() 
    
    while True:
        # Pulls the actual raw bytes from your fixed live.py singleton
        frame_bytes = receiver.get_latest_frame()
        
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            # Non-blocking sleep to match ~30 FPS and save CPU
            await asyncio.sleep(0.03) 
        else:
            # Non-blocking wait if the buffer is temporarily empty
            await asyncio.sleep(0.1)

async def video_feed(request):
    """
    The MJPEG stream endpoint for the frontend <img> tag.
    Now properly wrapped as an async view for ASGI/Daphne.
    """
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@csrf_exempt
def toggle_camera(request):
    """
    Synchronous endpoint to turn the drone's hardware stream on/off.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command')
            
            # Use getters to ensure singletons are ready
            client = get_drone_client()
            receiver = get_video_receiver()

            if command == 'streamon':
                client.send('streamon')
                receiver.start()
                return JsonResponse({"status": "success"})
            elif command == 'streamoff':
                client.send('streamoff')
                receiver.stop()
                return JsonResponse({"status": "success"})

            return JsonResponse({"status": "error", "message": "Invalid command"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)