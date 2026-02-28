import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.drone_runtime.services import status as drone_status, connect, send

@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"ok": True, "context": "xxxxxxxxx"})

@csrf_exempt
@require_http_methods(["GET"])
def drone_status_view(request):
    return JsonResponse(drone_status())

@csrf_exempt
@require_http_methods(["POST"])
def drone_connect_view(request):
    r = connect()
    
    return JsonResponse({
        "ok": r.get("ok", False), 
        "res": r.get("text", "Failed to connect")
    })