from django.urls import path
from . import views

urlpatterns = [
    path('active/', views.get_active_plan, name='mission_active'),
    path('<int:plan_id>/', views.patch_plan, name='mission_patch'),
    path('<int:plan_id>/steps/', views.add_step, name='mission_add_step'),
    path('<int:plan_id>/steps/clear/', views.clear_steps, name='mission_clear_steps'),
    path('steps/<int:step_id>/', views.delete_step, name='mission_delete_step'),
    
    path('run/', views.run_mission_view, name='mission_run'),
    path('status/', views.mission_status_view, name='mission_status'),
    path('override/', views.override_command_view, name='mission_override'),
]