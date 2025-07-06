# admin.py
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from .models import Referral
from audit.mixins import ExcelExportMixin

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('referrer', 'referred', 'referral_code', 'timestamp')
    search_fields = ('referrer__email', 'referred__email', 'referral_code')
    list_filter = ('timestamp',)
    actions = ['export_selected_to_excel']

    excel_export_fields = ['referrer__email', 'referred__email', 'referral_code', 'timestamp']
    excel_export_filename = 'referrals_export'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'export-referrals/',
                self.admin_site.admin_view(self.export_all_referrals_excel),
                name='export_referrals_excel'
            ),
        ]
        return custom_urls + urls

    def export_all_referrals_excel(self, request):
        queryset = self.model.objects.select_related('referrer', 'referred').all()
        return self.export_selected_to_excel(request, queryset)
