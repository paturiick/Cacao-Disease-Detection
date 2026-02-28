import json
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


# --- HARDWARE EXECUTION & OVERRIDE VIEWS ---

@csrf_exempt
@require_http_methods(["POST"])
def run_mission_view(request):
    """Triggered when you click 'Run Mission' on the frontend."""
    body = json.loads(request.body)
    # Pass the JSON steps to our mission service
    steps = body.get("steps", [])
    speed = body.get("flightParams", {}).get("speed", 30)
    
    return JsonResponse(services.start_hardware_mission(steps, speed))

@csrf_exempt
@require_http_methods(["POST"])
def override_command_view(request):
    """Triggered by the Emergency or Stop buttons."""
    body = json.loads(request.body)
    cmd = body.get("command")
    return JsonResponse(services.send_live_override(cmd))

@require_http_methods(["GET"])
def mission_status_view(request):
    """Polled by Vue ONLY when a mission is running to update the progress bar."""
    return JsonResponse(services.get_mission_progress())