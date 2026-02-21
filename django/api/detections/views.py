from django.http import JsonResponse


def detection_list(request):
    return JsonResponse({
        "ok": True,
        "detections": []
    })


def detection_detail(request, detection_id):
    return JsonResponse({
        "ok": True,
        "detection_id": detection_id,
        "class": None,
        "confidence": None,
        "lat": None,
        "lng": None
    })
