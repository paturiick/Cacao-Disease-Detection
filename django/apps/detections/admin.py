# apps/detections/admin.py
from django.contrib import admin
from django.apps import apps

# Get all models from the detections app
app_models = apps.get_app_config('detections').get_models()

# Auto-register every model
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass