import os
import sys
from django.apps import AppConfig

# --- THE SPAM BOUNCER CLASS ---
class StreamSpamBouncer:
    seen_ble = False
    seen_gps = False

    def __init__(self, original_stream):
        self.original_stream = original_stream

    def write(self, text):
        text_str = str(text)
        
        # Filter BLE Control successes
        if "/api/telemetry/ble-control/" in text_str and " 200 " in text_str:
            if StreamSpamBouncer.seen_ble:
                return  # Mute
            StreamSpamBouncer.seen_ble = True
            return self.original_stream.write(text) # Print the first one

        # Filter GPS successes
        if "/api/telemetry/gps/" in text_str and " 200 " in text_str:
            if StreamSpamBouncer.seen_gps:
                return  # Mute
            StreamSpamBouncer.seen_gps = True
            return self.original_stream.write(text) # Print the first one
            
        # Let everything else through
        return self.original_stream.write(text)

    def flush(self):
        self.original_stream.flush()

    def __getattr__(self, attr):
        return getattr(self.original_stream, attr)


class TelemetryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.telemetry"

    def ready(self):
        # 1. APPLY FILTER GLOBALLY FIRST! 
        # (This must happen before the RUN_MAIN check so Daphne gets it)
        if not isinstance(sys.stdout, StreamSpamBouncer):
            sys.stdout = StreamSpamBouncer(sys.stdout)
            sys.stderr = StreamSpamBouncer(sys.stderr)

        # 2. Prevent the sampler thread from running twice
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return
            
        # 3. Boot the sampler (Only runs in the Worker process)
        from .sampler import start_sampler
        print("BOOTING UP TELEMETRY SAMPLER...")
        start_sampler(sample_every_s=1.0)