import json
import asyncio
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from apps.drone_runtime.services import status as drone_status, connect, send

@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"ok": True, "context": "xxxxxxxxx"})

# Keep the original view for quick standard API checks
@csrf_exempt
@require_http_methods(["GET"])
def drone_status_view(request):
    return JsonResponse(drone_status())

@csrf_exempt
@require_http_methods(["POST"])
def drone_connect_view(request):
    r = connect()
    return JsonResponse({
        "ok": r.get("ok", False), 
        "res": r.get("text", "Failed to connect")
    })

# --- NEW SSE ENDPOINT ---
@sync_to_async
def get_async_drone_status():
    """Safely fetch the status in an async context."""
    return drone_status()

async def stream_drone_status(request):
    """
    SSE Endpoint: Keeps connection open and pushes drone connection status.
    """
    async def event_stream():
        last_status = None
        
        while True:
            current_status = await get_async_drone_status()
            is_connected = current_status.get("connected", False)
            
            # Only push data if the status changes (or on the very first check)
            if is_connected != last_status:
                yield f"data: {json.dumps(current_status)}\n\n"
                last_status = is_connected
                
            await asyncio.sleep(2.0) # Check every 2 seconds

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')