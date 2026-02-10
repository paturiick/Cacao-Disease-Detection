from django.urls import path
from . import views

urlpatterns = [
    path("fields/", views.field_list_create),
    path("fields/<int:field_id>/", views.field_detail),
    path("runs/<int:run_id>/path/", views.run_path_geojson),
    path("runs/<int:run_id>/detections/geojson/", views.run_detections_geojson),
]
