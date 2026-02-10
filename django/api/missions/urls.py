from django.urls import path
from . import views

urlpatterns = [
    path("", views.mission_list_create),                 # /api/missions/
    path("<int:mission_id>/", views.mission_detail),     # /api/missions/1/
    path("<int:mission_id>/start/", views.mission_start),# /api/missions/1/start/

    path("runs/", views.run_list),                       # /api/missions/runs/
    path("runs/<int:run_id>/", views.run_detail),        # /api/missions/runs/1/
    path("runs/<int:run_id>/abort/", views.run_abort),   # /api/missions/runs/1/abort/
]

