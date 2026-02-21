from django.http import JsonResponse


def run_stats(request, run_id):
    return JsonResponse({
        "run_id": run_id,
        "duration_sec": None,
        "distance_m": None,
        "avg_speed_mps": None,
        "battery_used_pct": None
    })


def run_detection_stats(request, run_id):
    return JsonResponse({
        "run_id": run_id,
        "detections_total": 0,
        "by_class": {},
        "by_severity": {}
    })
