# apps/detections/views.py
import json
import asyncio
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET
from asgiref.sync import sync_to_async
from .models import CacaoDetectionLog

@require_GET
def get_detection_stats(request):
    """
    Standard synchronous endpoint for one-time stat retrieval.
    """
    session_id = request.GET.get('session_id')
    log = CacaoDetectionLog.objects.filter(session_id=session_id).first()
    if not log:
        return JsonResponse({"status": "success", "healthy_count": 0, "unhealthy_count": 0, "pods": []})
    
    pods = list(log.detected_pods.values('track_id', 'status', 'last_seen'))
    return JsonResponse({
        "status": "success", 
        "healthy_count": log.healthy_count, 
        "unhealthy_count": log.unhealthy_count, 
        "pods": pods
    })

def get_log_data(session_id):
    """
    Synchronous helper to fetch detection data from the database.
    """
    log = CacaoDetectionLog.objects.filter(session_id=session_id).first()
    if log:
        # Add 'latitude', 'longitude', 'yaw', 'roll', and 'pitch' to this list
        pods = list(log.detected_pods.values(
            'track_id', 'status', 'last_seen', 'image', 
            'latitude', 'longitude', 'yaw', 'roll', 'pitch'
        ))
        return {
            'status': 'success',
            'healthy_count': log.healthy_count,
            'unhealthy_count': log.unhealthy_count,
            'pods': pods
        }
    return {'status': 'searching'}

async def stream_detection_stats(request):
    """
    Asynchronous SSE Endpoint: Pushes live AI counts to the Vue frontend without blocking.
    """
    session_id = request.GET.get('session_id')
    
    # Wrap the database helper in sync_to_async for safe execution in an async loop
    async_get_log_data = sync_to_async(get_log_data, thread_sensitive=True)

    async def event_stream():
        try:
            while True:
                # Fetch data asynchronously from the database
                data_dict = await async_get_log_data(session_id)
                
                # Format exactly as the Vue EventSource expects (data: <json>\n\n)
                data_json = json.dumps(data_dict, default=str)
                yield f"data: {data_json}\n\n"
                
                # Use non-blocking sleep so the server can handle other tasks
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            # Cleanly handle client disconnects (user leaves the page)
            print(f"[SSE] Client disconnected for session: {session_id}")
            raise

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')