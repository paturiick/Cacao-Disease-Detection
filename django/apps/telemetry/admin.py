from django.contrib import admin
from .models import LiveSystemState, TelemetrySnapshot

@admin.register(LiveSystemState)
class LiveSystemStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'ble_active', 'gps_lat', 'gps_lon', 'last_error')
    list_editable = ('ble_active',)  # Let's you toggle BLE directly from the list view!
    
    # Optional but recommended: 
    # Since LiveSystemState is meant to be a single-row table (id=1), 
    # this prevents you from accidentally clicking "Add" and creating a second row.
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


@admin.register(TelemetrySnapshot)
class TelemetrySnapshotAdmin(admin.ModelAdmin):
    # What columns show up in the main list view
    list_display = ('recorded_date', 'recorded_time', 'connected', 'battery', 'altitude_m', 'flight_time')
    
    # Adds a filter sidebar on the right
    list_filter = ('connected', 'recorded_date')
    
    # Adds a search bar at the top (searches inside the raw JSON payload)
    search_fields = ('raw', 'last_error')
    
    # How they are sorted by default
    ordering = ('-recorded_date', '-recorded_time')
    
    # Prevents you from accidentally editing the auto-generated timestamps
    readonly_fields = ('recorded_date', 'recorded_time')