from django.http import JsonResponse


# -------- Fields --------

def field_list_create(request):
    return JsonResponse({
        "ok": True,
        "fields": []
    })


def field_detail(request, field_id):
    return JsonResponse({
        "ok": True,
        "field_id": field_id,
        "geometry": None
    })


# -------- Geo data --------

def run_path_geojson(request, run_id):
    return JsonResponse({
        "type": "FeatureCollection",
        "features": []
    })


def run_detections_geojson(request, run_id):
    return JsonResponse({
        "type": "FeatureCollection",
        "features": []
    })
