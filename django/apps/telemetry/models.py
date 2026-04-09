from django.db import models

class LiveSystemState(models.Model):
    """A single-row table to hold live cross-process state."""
    id = models.IntegerField(primary_key=True, default=1) # Forces exactly one row
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    ble_active = models.BooleanField(default=False) # For your Web UI toggle button

    last_error = models.CharField(max_length=100, blank=True, null=True)

class TelemetrySnapshot(models.Model):
    recorded_at = models.DateTimeField(auto_now_add=True)
    connected = models.BooleanField(default=False)
    
    battery = models.IntegerField(null=True, blank=True)
    altitude_m = models.FloatField(null=True, blank=True)
    
    pitch = models.IntegerField(null=True, blank=True)
    roll = models.IntegerField(null=True, blank=True)
    yaw = models.IntegerField(null=True, blank=True)
    tof_cm = models.IntegerField(null=True, blank=True)
    temp_c = models.IntegerField(null=True, blank=True)
    templ_c = models.IntegerField(null=True, blank=True)
    
    vgx = models.IntegerField(null=True, blank=True)
    vgy = models.IntegerField(null=True, blank=True)
    vgz = models.IntegerField(null=True, blank=True)
    
    agx = models.FloatField(null=True, blank=True)
    agy = models.FloatField(null=True, blank=True)
    agz = models.FloatField(null=True, blank=True)
    
    baro = models.FloatField(null=True, blank=True)
    flight_time = models.IntegerField(null=True, blank=True)
    
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    
    raw = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["-recorded_at"]),
            models.Index(fields=["connected", "-recorded_at"]),
        ]