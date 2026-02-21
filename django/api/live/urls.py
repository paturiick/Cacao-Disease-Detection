from django.urls import path
from . import views

urlpatterns = [
    path("status/", views.live_status),
    path("telemetry/latest/", views.telemetry_latest),
    path("video/stream-info/", views.stream_info),
]
