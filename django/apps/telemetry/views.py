import asyncio
import json
import datetime
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder  
from asgiref.sync import sync_to_async
from .models import TelemetrySnapshot

TELEMETRY_FIELDS = [
    "recorded_date", "recorded_time", "connected", "battery", "altitude_m",
    "pitch", "roll", "yaw", "tof_cm", "temp_c", "templ_c",
    "vgx", "vgy", "vgz", "agx", "agy", "agz", 
    "baro", "flight_time", "gps_lat", "gps_lon",
    "gps_sats", "gps_status",
    "drone_snr", "esp32_rssi"
]

@require_http_methods(["GET"])
def latest(request):
    row = TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS).first()
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
    rows = list(TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS)[:limit])
    for row in rows:
        if row.get('recorded_date') and row.get('recorded_time'):
            dt = datetime.datetime.combine(row['recorded_date'], row['recorded_time'])
            row['recorded_at'] = dt.isoformat()
    return JsonResponse({"items": rows})

@sync_to_async
def get_latest_telemetry():
    row = TelemetrySnapshot.objects.values(*TELEMETRY_FIELDS).first()
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
                    json_data = json.dumps(data, cls=DjangoJSONEncoder)
                    yield f"data: {json_data}\n\n"
                    last_timestamp = current_timestamp
            await asyncio.sleep(0.5)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')