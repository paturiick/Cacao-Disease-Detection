# apps/missions/admin.py
from django.contrib import admin
from django.apps import apps

# Get all models from the missions app
app_models = apps.get_app_config('missions').get_models()

for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass