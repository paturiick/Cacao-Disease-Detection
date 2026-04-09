# apps/live/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.video_feed, name='live-video-feed'),
    path('toggle/', views.toggle_camera, name='toggle-camera'),
    path('record/', views.toggle_recording, name='toggle-recording'),
]