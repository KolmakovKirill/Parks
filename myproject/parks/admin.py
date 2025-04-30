from django.contrib import admin
from .models import UserData, LightZone, SystemLog


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'ssid')
    search_fields = ('user__username', 'ssid')

@admin.register(LightZone)
class LightZoneAdmin(admin.ModelAdmin):
    list_display = ('user', 'zone_number', 'is_on')
    list_filter = ('zone_number', 'is_on')
    search_fields = ('user__username',)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'zone_number', 'action')
    list_filter = ('zone_number', 'action', 'user')
    search_fields = ('user__username', 'zone_number')
    ordering = ('-timestamp',)