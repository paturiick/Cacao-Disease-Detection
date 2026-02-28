from django.urls import path, include

urlpatterns = [
    path("core/", include("apps.core.urls")),
    path("missions/", include("apps.missions.urls")),
    path("live/", include("apps.live.urls")),
    path("mapping/", include("apps.mapping.urls")),
    path("detections/", include("apps.detections.urls")),
    path("telemetry/", include("apps.telemetry.urls")),
    path("reports/", include("apps.reports.urls")),
]