from django.urls import path
from . import views

urlpatterns = [
    path('capture-pods/', views.stream_capture_pods, name='capture-pods-stream'),
]