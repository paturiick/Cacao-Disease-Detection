from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

# Corrected Imports
from .models import MissionPlan, MissionStep
from .serializers import MissionPlanSerializer, MissionStepSerializer

# Absolute imports often resolve "could not be resolved" errors better
from api.missions.runner import start_plan, trigger_emergency_land 

def get_or_create_active_plan():
    plan = MissionPlan.objects.order_by("-id").first()
    if not plan:
        plan = MissionPlan.objects.create()
    return plan

@api_view(["GET"])
def active_plan(request):
    plan = get_or_create_active_plan()
    return Response(MissionPlanSerializer(plan).data)

@api_view(["PATCH"])
def update_plan(request, plan_id: int):
    plan = MissionPlan.objects.get(id=plan_id)
    for field in ["altitude", "speed", "mode"]:
        if field in request.data:
            setattr(plan, field, request.data[field])
    plan.save()
    return Response(MissionPlanSerializer(plan).data)

@api_view(["POST"])
def add_step(request, plan_id: int):
    plan = MissionPlan.objects.get(id=plan_id)
    step_type = request.data.get("type")
    val = request.data.get("val")
    last = MissionStep.objects.filter(plan=plan).order_by("-order").first()
    next_order = (last.order + 1) if last else 1
    step = MissionStep.objects.create(
        plan=plan,
        order=next_order,
        type=step_type,
        val=float(val),
    )
    return Response(MissionStepSerializer(step).data, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
def delete_step(request, step_id: int):
    MissionStep.objects.filter(id=step_id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
def clear_steps(request, plan_id: int):
    plan = MissionPlan.objects.get(id=plan_id)
    MissionStep.objects.filter(plan=plan).delete()
    with transaction.atomic():
        plan.status = "inactive"
        plan.active_index = -1
        plan.message = "Cleared"
        plan.save()
    return Response({"detail": "cleared"})

@api_view(["POST"])
def force_land_view(request, plan_id):
    """API endpoint to cancel mission and land immediately."""
    try:
        plan = MissionPlan.objects.get(id=plan_id)
        # 1. Update DB Status immediately so polling reflects the change
        plan.status = "cancelled"
        plan.message = "EMERGENCY LANDING INITIATED"
        plan.save()
        
        # 2. Execute physical command using the newly imported runner function
        if trigger_emergency_land():
            return Response({"status": "success"})
        return Response({"status": "error", "message": "Drone unreachable"}, status=500)
    except MissionPlan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=404)

@api_view(["POST"])
def run_plan(request, plan_id: int):
    plan = MissionPlan.objects.get(id=plan_id)
    if plan.status in ("queued", "running"):
        return Response({"detail": "Already running/queued"}, status=409)
    with transaction.atomic():
        plan.status = "queued"
        plan.active_index = -1
        plan.message = "Queued"
        plan.save()
    start_plan(plan.id)
    return Response({"status": "queued", "plan_id": plan.id})

@api_view(["POST"])
def cancel_plan(request, plan_id: int):
    plan = MissionPlan.objects.get(id=plan_id)
    with transaction.atomic():
        plan.status = "cancelled"
        plan.message = "Cancel requested"
        plan.save()
    return Response({"status": "cancelled"})

@api_view(["GET"])
def plan_status(request, plan_id: int):
    plan = MissionPlan.objects.get(id=plan_id)
    return Response({
        "status": plan.status,
        "active_index": plan.active_index,
        "gps": plan.gps,
        "battery": plan.battery,
        "message": plan.message,
    })