from rest_framework import serializers
from .models import MissionPlan, MissionStep

class MissionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionStep
        fields = ["id", "order", "type", "val"]

class MissionPlanSerializer(serializers.ModelSerializer):
    steps = MissionStepSerializer(many=True, read_only=True)

    class Meta:
        model = MissionPlan
        fields = [
            "id", "name",
            "altitude", "speed", "mode",
            "status", "active_index", "message",
            "gps", "battery",
            "steps",
        ]