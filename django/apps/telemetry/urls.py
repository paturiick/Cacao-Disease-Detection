from django.urls import path
from . import views

urlpatterns = [
    path("latest/", views.latest),
    path("recent/", views.recent),
    path("stream/", views.stream_telemetry), 
]