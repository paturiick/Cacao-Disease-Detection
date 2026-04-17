# apps/reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.get_mission_history, name='mission-history'),
    path('mission/<int:mission_id>/', views.get_mission_report, name='mission-report'),
    path('mission/<int:mission_id>/delete/', views.delete_mission, name='mission-delete'),
]