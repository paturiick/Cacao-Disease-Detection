from django.http import JsonResponse

def mission_list_create(request):
    return JsonResponse({
        "ok": True,
        "endpoint": "missions list/create",
        "method": request.method
    })

def mission_detail(request, mission_id):
    return JsonResponse({
        "ok": True,
        "endpoint": "mission detail",
        "mission_id": mission_id
    })


def mission_start(request, mission_id):
    return JsonResponse({
        "ok": True,
        "endpoint": "mission start",
        "mission_id": mission_id,
        "run_id": 1
    })


# -------- Runs --------

def run_list(request):
    return JsonResponse({
        "ok": True,
        "endpoint": "runs list",
        "runs": []
    })


def run_detail(request, run_id):
    return JsonResponse({
        "ok": True,
        "endpoint": "run detail",
        "run_id": run_id,
        "status": "IDLE"
    })


def run_abort(request, run_id):
    return JsonResponse({
        "ok": True,
        "endpoint": "run abort",
        "run_id": run_id,
        "aborted": True
    })
