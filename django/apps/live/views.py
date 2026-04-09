# apps/live/views.py
import json
import asyncio
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drone_controller.instance import get_video_receiver, get_drone_client
from asgiref.sync import sync_to_async

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