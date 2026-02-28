from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import TelemetrySnapshot

# Updated list to include the new fields
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