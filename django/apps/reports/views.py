# apps/reports/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Max, Min
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from apps.missions.models import FlightPlan 
from apps.telemetry.models import MissionTelemetryLog
from apps.detections.models import CacaoDetectionLog

def get_mission_history(request):
    """
    Returns a lightweight list of missions for the Vue sidebar.
    """
    flights = FlightPlan.objects.all().order_by('-created_at')
    
    # Removed the bad 'session_id' field here!
    missions_data = [
        {
            "id": f.id, 
            "name": f.name, 
            "date": f.created_at.strftime("%Y-%m-%d")
        }
        for f in flights
    ]
    return JsonResponse({"missions": missions_data})

def get_mission_report(request, mission_id):
    """
    Master endpoint that aggregates Mission, Telemetry, and Detections.
    """
    mission = get_object_or_404(FlightPlan, id=mission_id)
    
    # 1. Find the linked session_id using the Detections Log as a bridge
    detection_log = CacaoDetectionLog.objects.filter(flight_plan_id=mission.id).first()
    session_id = detection_log.session_id if detection_log else None

    # 2. Telemetry Aggregation
    flight_time, max_alt, battery_end = 0, 0, 0
    if session_id:
        telemetry_logs = MissionTelemetryLog.objects.filter(session_id=session_id)
        flight_time = telemetry_logs.aggregate(Max('flight_time'))['flight_time__max'] or 0
        max_alt = telemetry_logs.aggregate(Max('altitude_m'))['altitude_m__max'] or 0
        battery_end = telemetry_logs.aggregate(Min('battery'))['battery__min'] or 0
    
    # 3. Detections & Map Aggregation
    detection_stats = {"total_pods": 0, "unhealthy": 0}
    trees_data = []

    if detection_log:
        detection_stats = {
            "total_pods": detection_log.healthy_count + detection_log.unhealthy_count,
            "unhealthy": detection_log.unhealthy_count
        }
        
        for pod in detection_log.detected_pods.all():
            trees_data.append({
                "tree_id": pod.track_id,
                "lat": float(pod.latitude) if pod.latitude else 8.49918,
                "lon": float(pod.longitude) if pod.longitude else 124.31046,
                "accuracy": 95 if pod.status == 'healthy' else 88, 
                "image": f"{request.scheme}://{request.get_host()}/media/{pod.image}" if pod.image else None
            })

    # 4. Flight Sequence
    steps_data = []
    for step in mission.steps.all().order_by('order'):
        steps_data.append({
            "step_id": step.id,
            "order": step.order,
            "command": step.step_type,  # <-- Uses your exact model field
            "value": step.step_val      # <-- Uses your exact model field
        })

    # 5. Final Payload Assembly
    payload = {
        "id": mission.id,
        "name": mission.name,
        "altitude_m": getattr(mission, 'altitude', 0),
        "speed": getattr(mission, 'speed', 30),
        "mode": "Stabilize", 
        "date": mission.created_at.strftime("%Y-%m-%d"),
        "telemetry": {
            "recorded_at": mission.created_at.strftime("%Y-%m-%d"),
            "battery_end": battery_end,
            "max_altitude": float(max_alt),
            "flight_time": flight_time,
        },
        "detection": detection_stats,
        "trees": trees_data,
        "steps": steps_data
    }

    return JsonResponse(payload)

@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_mission(request, mission_id):
    """
    Deletes a specific mission (FlightPlan) and returns a confirmation payload.
    """
    mission = get_object_or_404(FlightPlan, id=mission_id)
    
    mission.delete()
    
    return JsonResponse({
        "status": "success",
        "message": f"Mission {mission_id} has been deleted.",
        "id": mission_id
    }, status=200)