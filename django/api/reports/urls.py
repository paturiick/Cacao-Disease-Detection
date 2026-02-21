from django.urls import path
from . import views

urlpatterns = [
    path("runs/<int:run_id>/stats/", views.run_stats),
    path("runs/<int:run_id>/detections/stats/", views.run_detection_stats),
]
