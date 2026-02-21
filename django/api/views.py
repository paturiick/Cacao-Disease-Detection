from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from api.missions.models import MissionPlan
from api.missions.runner import trigger_emergency_land

@api_view(["POST"])
def force_land_view(request, plan_id):
    """
    API endpoint to abort the mission and force the drone to land.
    """
    try:
        with transaction.atomic():
            plan = MissionPlan.objects.select_for_update().get(id=plan_id)
            plan.status = "cancelled"
            plan.message = "EMERGENCY: Force Landing Initiated"
            plan.save()
        
        # Execute the physical drone command
        success = trigger_emergency_land()
        
        if success:
            return Response({"status": "success", "message": "Landing command sent"})
        else:
            return Response({"status": "error", "message": "Drone unresponsive"}, status=500)
            
    except MissionPlan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=404)

@api_view(["GET"])
def health(request):
    """Simple health check endpoint to verify the API is running."""
    return Response({"status": "healthy", "message": "API is running smoothly."})