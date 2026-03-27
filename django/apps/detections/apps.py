# apps/detections/apps.py
from django.apps import AppConfig
import os

class DetectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.detections'

    def ready(self):
        # This prevents Django from starting two AI threads when the auto-reloader runs
            from .inference import start_inference_loop
            start_inference_loop()