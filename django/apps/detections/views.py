# apps/detections/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CacaoDetectionLog

@require_GET
def get_detection_stats(request):
    """
    Returns the total healthy/unhealthy counts and a list of all individual pods for a specific flight.
    """
    session_id = request.GET.get('session_id')
    
    if not session_id:
         return JsonResponse({"status": "error", "message": "Missing session_id parameter"}, status=400)

    log = CacaoDetectionLog.objects.filter(session_id=session_id).first()
    
    if not log:
        # Return zeros if the session just started and nothing is detected yet
        return JsonResponse({
            "status": "success",
            "session_id": session_id,
            "healthy_count": 0,
            "unhealthy_count": 0,
            "pods": []
        })

    # Grab all the individual pods linked to this session
    pods = list(log.detected_pods.values('track_id', 'status', 'last_seen'))
        
    return JsonResponse({
        "status": "success",
        "session_id": session_id,
        "healthy_count": log.healthy_count,
        "unhealthy_count": log.unhealthy_count,
        "pods": pods
    })