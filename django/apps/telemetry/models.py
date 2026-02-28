from django.db import models

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
    
    # New: Velocity
    vgx = models.IntegerField(null=True, blank=True)
    vgy = models.IntegerField(null=True, blank=True)
    vgz = models.IntegerField(null=True, blank=True)
    
    # New: Acceleration
    agx = models.FloatField(null=True, blank=True)
    agy = models.FloatField(null=True, blank=True)
    agz = models.FloatField(null=True, blank=True)
    
    # New: Environment & Time
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