import json
import asyncio
from django.http import StreamingHttpResponse
from asgiref.sync import sync_to_async
from apps.detections.models import CacaoDetectionLog

@sync_to_async
def get_map_data(session_id):
    # DUAL-MODE LOGIC:
    # If the frontend asks for 'latest', grab the most recent flight
    if session_id == 'latest':
        log = CacaoDetectionLog.objects.order_by('-start_time').first()
    # Otherwise, grab the specific historical flight they asked for
    else:
        log = CacaoDetectionLog.objects.filter(session_id=session_id).first()
        
    if not log: 
        return None
    
    return {
        "healthy": log.healthy_count,
        "unhealthy": log.unhealthy_count,
        "pods": list(log.detected_pods.values('track_id', 'status', 'image', 'latitude', 'longitude', 'first_seen'))
    }

async def stream_capture_pods(request):
    session_id = request.GET.get('session_id')
    
    async def event_stream():
        last_count = -1
        while True:
            data = await get_map_data(session_id)
            if data and len(data['pods']) != last_count:
                yield f"data: {json.dumps(data, default=str)}\n\n"
                last_count = len(data['pods'])
            await asyncio.sleep(1.0)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')