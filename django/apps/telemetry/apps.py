import os
import sys
from django.apps import AppConfig

class StreamSpamBouncer:
    def __init__(self, original_stream):
        self.original_stream = original_stream

    def write(self, text):
        # General filter for common telemetry successes if needed
        return self.original_stream.write(text)

    def flush(self):
        self.original_stream.flush()

    def __getattr__(self, attr):
        return getattr(self.original_stream, attr)

class TelemetryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.telemetry"

    def ready(self):
        if not isinstance(sys.stdout, StreamSpamBouncer):
            sys.stdout = StreamSpamBouncer(sys.stdout)
            sys.stderr = StreamSpamBouncer(sys.stderr)

        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return
            
        from .sampler import start_sampler
        print("BOOTING UP NATIVE TELEMETRY SAMPLER...")
        start_sampler(sample_every_s=1.0)