from django.contrib import admin
from .models import LiveSystemState, TelemetrySnapshot, MissionTelemetryLog

@admin.register(LiveSystemState)
class LiveSystemStateAdmin(admin.ModelAdmin):
    # Removed ble_active and last_error from list_display and list_editable
    list_display = ('id', 'gps_lat', 'gps_lon')
    
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(TelemetrySnapshot)
class TelemetrySnapshotAdmin(admin.ModelAdmin):
    list_display = ('recorded_date', 'recorded_time', 'connected', 'battery', 'drone_snr', 'esp32_rssi', 'altitude_m', 'gps_sats', 'gps_status')
    list_filter = ('connected', 'recorded_date', 'gps_status')
    search_fields = ('raw',)
    ordering = ('-recorded_date', '-recorded_time')
    readonly_fields = ('recorded_date', 'recorded_time')

@admin.register(MissionTelemetryLog)
class MissionTelemetryLogAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'recorded_at', 'battery', 'altitude_m', 'gps_lat', 'gps_lon')
    list_filter = ('recorded_at', 'session_id')
    search_fields = ('session_id',)
    ordering = ('-recorded_at',)