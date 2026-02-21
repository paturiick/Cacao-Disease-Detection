from django.db import models

class MissionPlan(models.Model):
    STATUS_CHOICES = [
        ("inactive", "inactive"),
        ("queued", "queued"),
        ("running", "running"),
        ("completed", "completed"),
        ("failed", "failed"),
        ("cancelled", "cancelled"),
    ]

    name = models.CharField(max_length=120, blank=True, default="Active Plan")

    # matches your frontend flightParams
    altitude = models.FloatField(default=100.0)  # metres
    speed = models.FloatField(default=15.0)      # m/s
    mode = models.CharField(max_length=40, default="Stabilize")

    # mission runtime state for UI
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="inactive")
    active_index = models.IntegerField(default=-1)  # -1 idle, 0 init, 1..n steps
    message = models.CharField(max_length=255, blank=True, default="")

    # telemetry snapshot for right-side cards
    gps = models.CharField(max_length=20, default="Weak")
    battery = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MissionStep(models.Model):
    plan = models.ForeignKey(MissionPlan, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField(default=1)

    # matches your dropdown: up/down/left/right/forward/back/cw/ccw/hover
    type = models.CharField(max_length=20)
    val = models.FloatField(default=1.0)  # seconds (for now)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]