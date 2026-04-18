# apps/live/views.py
import json
import asyncio
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drone_controller.instance import get_video_receiver, get_drone_client
from asgiref.sync import sync_to_async

STANDBY_FRAME = (
    b'\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x00\xff\xd9'
)

async def generate_frames():
    receiver = get_video_receiver() 
    
    while True:
        frame_bytes = receiver.get_latest_frame()
        
        if not frame_bytes:
            frame_bytes = STANDBY_FRAME
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Non-blocking sleep to match ~30 FPS
        await asyncio.sleep(0.03)

async def video_feed(request):
    """
    The MJPEG stream endpoint for the frontend <img> tag.
    Now properly wrapped as an async view for ASGI/Daphne.
    """
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def _handle_hardware_toggle(command):
    client = get_drone_client()
    receiver = get_video_receiver()

    if command == 'streamon':
        reply = client.send('streamon') # This socket call blocks!
        if reply.ok:
            receiver.start()
        return reply
    elif command == 'streamoff':
        reply = client.send('streamoff') # This socket call blocks!
        receiver.stop()
        return reply
    return None
# ---------------------------


@csrf_exempt
async def toggle_camera(request):
    """
    Now properly async. The blocking hardware call is safely threaded.
    """
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            command = data.get('command')
            
            # Run the blocking function in a background thread
            reply = await sync_to_async(_handle_hardware_toggle, thread_sensitive=False)(command)

            if reply and reply.ok:
                return JsonResponse({"status": "success"})
            elif reply:
                return JsonResponse({"status": "error", "message": reply.text}, status=400)
            else:
                return JsonResponse({"status": "error", "message": "Invalid command"}, status=400)
                
        # Catch the DroneTimeout error specifically so it doesn't crash the server
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def toggle_recording(request):
    """
    Endpoint to start/stop saving the stream to an MP4 file.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command')
            receiver = get_video_receiver()

            if command == 'start':
                receiver.start_recording()
                return JsonResponse({"status": "success", "message": "Recording started"})
            
            elif command == 'stop':
                receiver.stop_recording()
                return JsonResponse({"status": "success", "message": "Recording stopped"})

            return JsonResponse({"status": "error", "message": "Invalid command"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)