# apps/detections/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CacaoDetectionLog

@require_GET  # This ensures the view instantly rejects anything that isn't a GET request
def get_detection_stats(request):
    """
    Returns the latest 20 detection logs.
    """
    # Fetch the most recent 20 logs, ordered by newest first
    logs = CacaoDetectionLog.objects.order_by('-timestamp')[:20]
    
    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "healthy_count": log.healthy_count,
            "unhealthy_count": log.unhealthy_count
        })
        
    return JsonResponse({
        "status": "success",
        "total_records_returned": len(data),
        "data": data
    })