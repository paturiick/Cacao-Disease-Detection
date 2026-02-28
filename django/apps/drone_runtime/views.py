from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import services

@csrf_exempt 
@require_http_methods(["POST"])
def connect_drone_view(request):
    return JsonResponse(services.connect())

@require_http_methods(["GET"])
def drone_status_view(request):
    return JsonResponse(services.status())