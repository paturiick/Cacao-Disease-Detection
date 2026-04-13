from django.db import models

class MissionTelemetryLog(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    
    # Core Hardware Data
    battery = models.IntegerField(null=True, blank=True)
    altitude_m = models.FloatField(null=True, blank=True)
    flight_time = models.IntegerField(null=True, blank=True)
    
    # Orientation & Environment (Crucial for proving stability in your thesis)
    pitch = models.IntegerField(null=True, blank=True)
    roll = models.IntegerField(null=True, blank=True)
    yaw = models.IntegerField(null=True, blank=True)
    temp_c = models.IntegerField(null=True, blank=True)
    
    # GPS injected from your LiveSystemState
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['recorded_at']

    def __str__(self):
        return f"[{self.session_id}] Bat:{self.battery}% Alt:{self.altitude_m}m"

class LiveSystemState(models.Model):
    """A single-row table to hold live cross-process state."""
    id = models.IntegerField(primary_key=True, default=1) # Forces exactly one row
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    ble_active = models.BooleanField(default=False) # For your Web UI toggle button

    last_error = models.CharField(max_length=100, blank=True, null=True)

class TelemetrySnapshot(models.Model):
    recorded_date = models.DateField(auto_now_add=True)
    recorded_time = models.TimeField(auto_now_add=True)
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
        ordering = ["-recorded_date", "-recorded_time"]
        indexes = [
            models.Index(fields=["-recorded_date", "-recorded_time"]),
            models.Index(fields=["connected", "-recorded_date", "-recorded_time"]),
        ]