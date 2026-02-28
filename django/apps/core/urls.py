from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),
    path("drone/status/", views.drone_status_view),
    path("drone/connect/", views.drone_connect_view),
]