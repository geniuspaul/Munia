from django.contrib import admin
from .models import User, UserProfile, OTP
from audit.mixins import ExcelExportMixin

@admin.register(User)
class UserAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email',)
    ordering = ('-date_joined',)
    actions = ['export_selected_to_excel']

    excel_export_fields = ['email', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    excel_export_headers = ['Email', 'Active', 'Staff', 'Superuser', 'Joined']
    excel_export_filename = 'users_export'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('user', 'country', 'is_verified', 'referral_code', 'used_referral_code', 'created_at')
    search_fields = ('user__email', 'referral_code', 'used_referral_code', 'country')
    list_filter = ('country', 'is_verified')
    actions = ['export_selected_to_excel']

    excel_export_fields = [
        'user__email', 'country', 'is_verified', 'referral_code',
        'used_referral_code', 'ip_address', 'device_info', 'created_at'
    ]
    excel_export_headers = [
        'Email', 'Country', 'Verified?', 'Referral Code',
        'Used Referral Code', 'IP Address', 'Device Info', 'Created At'
    ]
    excel_export_filename = "user_profiles_export"


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('email', 'code', 'created_at', 'expires_at')
    search_fields = ('email', 'code')
    list_filter = ('created_at',)
    actions = ['export_selected_to_excel']

    excel_export_fields = ['email', 'code', 'created_at', 'expires_at']
    excel_export_headers = ['Email', 'Code', 'Created At', 'Expires At']
    excel_export_filename = "otp_export"
