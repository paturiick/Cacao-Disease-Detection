from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # The URL your Nuxt app will connect to: ws://localhost:8000/ws/video-feed/
    re_path(r'ws/video-feed/$', consumers.DroneVideoConsumer.as_asgi()),
]