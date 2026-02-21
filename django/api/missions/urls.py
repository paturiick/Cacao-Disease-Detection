from django.urls import path
from . import views

urlpatterns = [
    path("active/", views.active_plan),

    path("plans/<int:plan_id>/", views.update_plan),
    path("plans/<int:plan_id>/steps/", views.add_step),
    path("steps/<int:step_id>/", views.delete_step),
    path("plans/<int:plan_id>/steps/clear/", views.clear_steps),

    path("plans/<int:plan_id>/run/", views.run_plan),
    path("plans/<int:plan_id>/cancel/", views.cancel_plan),
    path("plans/<int:plan_id>/status/", views.plan_status),
]