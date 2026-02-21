from django.apps import AppConfig
import os

class MissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.missions'

    def ready(self):
        # Prevent the worker from starting twice in dev mode
        if os.environ.get('RUN_MAIN') == 'true':
            from .telemetry import start_telemetry_worker
            start_telemetry_worker()