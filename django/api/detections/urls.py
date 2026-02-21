from django.urls import path
from . import views

urlpatterns = [
    path("", views.detection_list),
    path("<int:detection_id>/", views.detection_detail),
]
