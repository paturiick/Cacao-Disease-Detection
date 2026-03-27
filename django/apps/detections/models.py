# apps/detections/models.py
import uuid
from django.db import models

class CacaoDetectionLog(models.Model):
    session_id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, db_index=True)
    start_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    healthy_count = models.IntegerField(default=0)
    unhealthy_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"[{self.session_id[-6:]}] Healthy: {self.healthy_count} | Unhealthy: {self.unhealthy_count}"

# --- NEW: Table for individual cacao pods ---
class DetectedCacao(models.Model):
    # This links the pod directly to the specific flight session
    session = models.ForeignKey(CacaoDetectionLog, related_name='detected_pods', on_delete=models.CASCADE)
    
    # The unique ID assigned by the BoT-SORT tracker
    track_id = models.IntegerField() 
    
    # 'healthy' or 'unhealthy'
    status = models.CharField(max_length=20) 
    
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        # A track_id is only unique within its specific session
        unique_together = ('session', 'track_id') 

    def __str__(self):
        return f"Session {self.session.session_id[-6:]} | Pod ID: {self.track_id} | Status: {self.status}"