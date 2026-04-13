import asyncio
import json
import datetime
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder  # <-- 1. NEW IMPORT
from asgiref.sync import sync_to_async
from .models import TelemetrySnapshot, LiveSystemState

# UPDATED FIELDS: Replaced "recorded_at" with "recorded_date" and "recorded_time"
TELEMETRY_FIELDS = [
    "recorded_date", "recorded_time", "connected", "battery", "altitude_m",
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
    
    # Re-inject 'recorded_at' for the frontend
    if row and row.get('recorded_date') and row.get('recorded_time'):
        dt = datetime.datetime.combine(row['recorded_date'], row['recorded_time'])
        row['recorded_at'] = dt.isoformat()
        
    return JsonResponse(row or {}, safe=False)

@require_http_methods(["GET"])
def recent(request):
    try:
        limit = int(request.GET.get("limit", "300"))
    except Exception:
        limit = 300
    limit = max(1, min(limit, 5000))
    rows = list(TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS)[:limit])
    
    # Re-inject 'recorded_at' for the frontend on all rows
    for row in rows:
        if row.get('recorded_date') and row.get('recorded_time'):
            dt = datetime.datetime.combine(row['recorded_date'], row['recorded_time'])
            row['recorded_at'] = dt.isoformat()

    return JsonResponse({"items": rows, "context": "xxxxxxxxx"})

@sync_to_async
def get_latest_telemetry():
    row = TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS).first()
    
    # Combine date and time into an ISO format string
    if row and row.get('recorded_date') and row.get('recorded_time'):
        dt = datetime.datetime.combine(row['recorded_date'], row['recorded_time'])
        row['recorded_at'] = dt.isoformat()
        
    return row

async def stream_telemetry(request):
    async def event_stream():
        last_timestamp = None
        while True:
            data = await get_latest_telemetry()
            if data:
                current_timestamp = data.get('recorded_at')
                if current_timestamp != last_timestamp:
                    # 2. UPDATED LOGIC: Tell json.dumps how to handle Date/Time objects
                    json_data = json.dumps(data, cls=DjangoJSONEncoder)
                    yield f"data: {json_data}\n\n"
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
    """Handles the Web UI toggle switch and error reporting."""
    state = get_system_state()
    
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            
            # If the script reports an error, we turn 'active' OFF
            # and save the error message.
            state.ble_active = payload.get("active", False)
            state.last_error = payload.get("error", None) 
            state.save()
            
            return JsonResponse({
                "status": "success", 
                "active": state.ble_active,
                "error": state.last_error
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
    # When the frontend calls GET, it sees both the state AND the error
    return JsonResponse({
        "active": state.ble_active,
        "error": state.last_error
    })