# admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SuspiciousActivityLog, UserDevice
from .mixins import ExcelExportMixin


@admin.register(SuspiciousActivityLog)
class SuspiciousActivityLogAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('user', 'activity_type', 'detected_at', 'resolved')
    list_filter = ('activity_type', 'resolved')
    search_fields = ('user__email', 'description')
    actions = ['mark_as_resolved', 'export_selected_to_excel']

    excel_export_fields = ['user', 'activity_type', 'description', 'detected_at', 'resolved']
    excel_export_filename = 'suspicious_logs_export'

    @admin.action(description="Mark selected logs as resolved")
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(resolved=True)
        self.message_user(request, f"{updated} log(s) marked as resolved.")


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('user', 'device_id', 'os', 'browser', 'last_used', 'is_trusted')
    list_filter = ('is_trusted', 'os', 'browser')
    search_fields = ('user__email', 'device_id')
    actions = ['export_selected_to_excel']

    excel_export_fields = ['user', 'device_id', 'os', 'browser', 'last_used', 'is_trusted']
    excel_export_filename = 'user_devices_export'
