# apps/detections/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.get_detection_stats, name='detection-stats'),
]