# apps/detections/models.py
import uuid
from django.db import models

class CacaoDetectionLog(models.Model):
    flight_plan_id = models.IntegerField(null=True, blank=True, db_index=True)
    session_id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, db_index=True)
    start_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    healthy_count = models.IntegerField(default=0)
    unhealthy_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"[{self.session_id[-6:]}] Healthy: {self.healthy_count} | Unhealthy: {self.unhealthy_count}"

class DetectedCacao(models.Model):

    session = models.ForeignKey(CacaoDetectionLog, related_name='detected_pods', on_delete=models.CASCADE)
    track_id = models.IntegerField() 
    status = models.CharField(max_length=20)  

    image = models.ImageField(upload_to='detections/', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    yaw = models.FloatField(null=True, blank=True)
    roll = models.FloatField(null=True, blank=True)
    pitch = models.FloatField(null=True, blank=True)
    
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        # A track_id is only unique within its specific session
        unique_together = ('session', 'track_id') 

    def __str__(self):
        return f"Session {self.session.session_id[-6:]} | Pod ID: {self.track_id} | Status: {self.status}"