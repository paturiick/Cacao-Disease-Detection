# apps/missions/views.py
import json
import uuid
from django.utils import timezone

from drone_controller.instance import get_video_receiver, get_telemetry_receiver
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import services
from .models import FlightPlan, FlightStep

def _serialize_plan(plan):
    steps = list(plan.steps.values('id', 'order', 'step_type', 'step_val'))
    formatted_steps = [
        {"id": s["id"], "order": s["order"], "type": s["step_type"], "val": s["step_val"]} 
        for s in steps
    ]
    return {
        "id": plan.id,
        "name": plan.name,
        "altitude": plan.altitude,
        "speed": plan.speed,
        "mode": plan.mode,
        "steps": formatted_steps
    }

@require_http_methods(["GET"])
def get_active_plan(request):
    plan, _ = FlightPlan.objects.get_or_create(is_active=True)
    return JsonResponse(_serialize_plan(plan))

@csrf_exempt
@require_http_methods(["PATCH"])
def patch_plan(request, plan_id):
    try:
        plan = FlightPlan.objects.get(id=plan_id)
        body = json.loads(request.body)
        if 'altitude' in body: plan.altitude = body['altitude']
        if 'speed' in body: plan.speed = body['speed']
        if 'mode' in body: plan.mode = body['mode']
        plan.save()
        return JsonResponse({"ok": True})
    except FlightPlan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def add_step(request, plan_id):
    try:
        plan = FlightPlan.objects.get(id=plan_id)
        body = json.loads(request.body)
        next_order = plan.steps.count()
        step = FlightStep.objects.create(
            plan=plan,
            order=next_order,
            step_type=body.get("type", "hover"),
            step_val=str(body.get("val", "0"))
        )
        return JsonResponse({
            "id": step.id, "type": step.step_type, "val": step.step_val, "order": step.order
        })
    except FlightPlan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_step(request, step_id):
    FlightStep.objects.filter(id=step_id).delete()
    return JsonResponse({"ok": True})

@csrf_exempt
@require_http_methods(["POST"])
def clear_steps(request, plan_id):
    FlightStep.objects.filter(plan_id=plan_id).delete()
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
def override_command_view(request):
    """Triggered by the Emergency or Stop buttons."""
    body = json.loads(request.body)
    cmd = body.get("command")

    if cmd in ["stop", "land", "emergency"]:
        receiver = get_video_receiver()
        receiver.current_plan_id = None

    return JsonResponse(services.send_live_override(cmd))

@require_http_methods(["GET"])
def mission_status_view(request):
    """Polled by Vue ONLY when a mission is running to update the progress bar."""
    return JsonResponse(services.get_mission_progress())


@csrf_exempt
@require_http_methods(["POST"])
def run_mission_view(request):
    """Triggered when you click 'Run Mission' on the frontend."""
    body = json.loads(request.body)
    steps = body.get("steps", [])
    speed = body.get("flightParams", {}).get("speed", 30)
    
    active_plan = FlightPlan.objects.filter(is_active=True).first()

    if not steps and active_plan:
        for step in active_plan.steps.all():
            steps.append({
                "type": step.step_type,
                "val": step.step_val
            })

    if not steps:
        return JsonResponse({"ok": False, "text": "No flight steps provided or found."})

    historical_plan = FlightPlan.objects.create(
        name=f"Flight Log: {timezone.now().strftime('%b %d, %H:%M')}",
        altitude=active_plan.altitude if active_plan else 2,
        speed=speed,
        mode=active_plan.mode if active_plan else "Stabilize",
        is_active=False 
    )

    
    for i, step_data in enumerate(steps):
        FlightStep.objects.create(
            plan=historical_plan,
            order=i,
            step_type=step_data.get("type", step_data.get("command", "")),
            step_val=step_data.get("val", step_data.get("value", ""))
        )

    new_session_id = str(uuid.uuid4())
    
    receiver = get_video_receiver()
    receiver.current_session_id = new_session_id
    receiver.current_plan_id = historical_plan.id

    telemetry = get_telemetry_receiver()
    telemetry.current_session_id = new_session_id
    
    result = services.start_hardware_mission(steps, speed)    
    result["session_id"] = new_session_id 
    
    return JsonResponse(result)