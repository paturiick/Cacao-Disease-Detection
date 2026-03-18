# apps/detections/models.py
import uuid
from django.db import models

class CacaoDetectionLog(models.Model):
    session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    healthy_count = models.IntegerField(default=0)
    unhealthy_count = models.IntegerField(default=0)
    
    # You can add more fields later, like the specific mission ID or GPS coordinates
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] Healthy: {self.healthy_count} | Unhealthy: {self.unhealthy_count}"