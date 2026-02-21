from django.http import JsonResponse


def live_status(request):
    return JsonResponse({
        "state": "OK",
        "connected": False,
        "current_run": None,
        "battery": None
    })


def telemetry_latest(request):
    return JsonResponse({
        "timestamp": None,
        "lat": None,
        "lng": None,
        "altitude_m": None,
        "battery_pct": None
    })


def stream_info(request):
    return JsonResponse({
        "type": "rtsp",
        "url": None,
        "note": "stream not configured yet"
    })
