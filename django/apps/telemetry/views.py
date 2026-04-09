import asyncio
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from .models import TelemetrySnapshot, LiveSystemState

TELEMETRY_FIELDS = [
    "recorded_at", "connected", "battery", "altitude_m",
    "pitch", "roll", "yaw", "tof_cm", "temp_c", "templ_c",
    "vgx", "vgy", "vgz", "agx", "agy", "agz", 
    "baro", "flight_time", "gps_lat", "gps_lon"
]

def get_system_state():
    """Helper to safely grab the single state row."""
    state, created = LiveSystemState.objects.get_or_create(id=1)
    return state

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

@sync_to_async
def get_latest_telemetry():
    row = TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS).first()
    if row and 'recorded_at' in row and row['recorded_at']:
        row['recorded_at'] = row['recorded_at'].isoformat()
    return row

async def stream_telemetry(request):
    async def event_stream():
        last_timestamp = None
        while True:
            data = await get_latest_telemetry()
            if data:
                current_timestamp = data.get('recorded_at')
                if current_timestamp != last_timestamp:
                    yield f"data: {json.dumps(data)}\n\n"
                    last_timestamp = current_timestamp
            await asyncio.sleep(0.5)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


# --- NEW HARDWARE ENDPOINTS ---

@csrf_exempt
@require_http_methods(["POST"])
def update_gps_endpoint(request):
    """Receives data from Windows and saves it to Postgres."""
    try:
        payload = json.loads(request.body)
        if "lat" in payload and "lng" in payload:
            state = get_system_state()
            state.gps_lat = payload["lat"]
            state.gps_lon = payload["lng"]
            state.save()
            return JsonResponse({"status": "synced"})
        elif "status" in payload:
            return JsonResponse({"status": "searching", "sats": payload.get("sats", 0)})
        return JsonResponse({"status": "ignored"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def ble_control(request):
    """Handles the Web UI toggle switch."""
    state = get_system_state()
    
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            state.ble_active = payload.get("active", False)
            state.save()
            return JsonResponse({"status": "success", "active": state.ble_active})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
    return JsonResponse({"active": state.ble_active})