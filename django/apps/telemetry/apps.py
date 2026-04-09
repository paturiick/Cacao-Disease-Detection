import os
import sys
from django.apps import AppConfig

class TelemetryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.telemetry"

    def ready(self):
        # Allow it to run in Docker, but prevent double-execution in 'manage.py runserver'
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return
            
        from .sampler import start_sampler
        print("BOOTING UP TELEMETRY SAMPLER...")
        start_sampler(sample_every_s=1.0)