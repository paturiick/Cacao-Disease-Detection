import os
from django.apps import AppConfig

class TelemetryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.telemetry"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return
        from .sampler import start_sampler
        start_sampler(sample_every_s=1.0)