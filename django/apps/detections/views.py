# apps/detections/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Sum
from .models import CacaoDetectionLog

@require_GET
def get_detection_stats(request):
    """
    Returns the total healthy and unhealthy counts for a specific flight session.
    """
    session_id = request.GET.get('session_id')
    
    if not session_id:
         return JsonResponse({
             "status": "error", 
             "message": "Missing session_id parameter"
         }, status=400)

    flight_logs = CacaoDetectionLog.objects.filter(session_id=session_id)
    
    totals = flight_logs.aggregate(
        total_healthy=Sum('healthy_count'),
        total_unhealthy=Sum('unhealthy_count')
    )
    
    healthy_total = totals['total_healthy'] or 0
    unhealthy_total = totals['total_unhealthy'] or 0
        
    return JsonResponse({
        "status": "success",
        "session_id": session_id,
        "healthy_count": healthy_total,
        "unhealthy_count": unhealthy_total
    })