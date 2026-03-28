import asyncio
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async
from .models import TelemetrySnapshot

TELEMETRY_FIELDS = [
    "recorded_at", "connected", "battery", "altitude_m",
    "pitch", "roll", "yaw", "tof_cm", "temp_c", "templ_c",
    "vgx", "vgy", "vgz", "agx", "agy", "agz", 
    "baro", "flight_time", "gps_lat", "gps_lon"
]

@require_http_methods(["GET"])
def latest(request):
    row = TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS).first()
    return JsonResponse(row or {}, safe=False)

@require_http_methods(["GET"])
def recent(request):
    try:
        limit = int(request.GET.get("limit", "300"))
    except Exception:
        limit = 300
        
    limit = max(1, min(limit, 5000))
    rows = list(TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS)[:limit])
    
    return JsonResponse({"items": rows, "context": "xxxxxxxxx"})


# --- NEW SSE ENDPOINT ---

@sync_to_async
def get_latest_telemetry():
    """Helper to safely fetch the newest DB row in an async loop."""
    row = TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS).first()
    if row and 'recorded_at' in row and row['recorded_at']:
        # Datetimes must be converted to strings for JSON
        row['recorded_at'] = row['recorded_at'].isoformat()
    return row

async def stream_telemetry(request):
    """
    SSE Endpoint: Keeps the connection open and pushes new telemetry data.
    """
    async def event_stream():
        last_timestamp = None
        
        while True:
            data = await get_latest_telemetry()
            
            if data:
                current_timestamp = data.get('recorded_at')
                
                # Only push the data if it is actually a new row from the drone
                if current_timestamp != last_timestamp:
                    yield f"data: {json.dumps(data)}\n\n"
                    last_timestamp = current_timestamp
            
            # Check the database twice a second (0.5s) for instant UI response
            await asyncio.sleep(0.5)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')