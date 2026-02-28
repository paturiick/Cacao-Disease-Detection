from django.db import models

class FlightPlan(models.Model):
    name = models.CharField(max_length=100, default="Active Mission")
    altitude = models.IntegerField(default=2)
    speed = models.IntegerField(default=30)
    mode = models.CharField(max_length=50, default="Stabilize")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan {self.id}: {self.name}"

class FlightStep(models.Model):
    plan = models.ForeignKey(FlightPlan, related_name='steps', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    
    # e.g., 'forward', 'cw', 'go', 'hover'
    step_type = models.CharField(max_length=50) 
    
    # e.g., '100' or '100 0 50 30'
    step_val = models.CharField(max_length=255, default="0") 

    class Meta:
        ordering = ['order'] # Ensures the Vue frontend always gets them in the right sequence

    def __str__(self):
        return f"{self.step_type} -> {self.step_val}"