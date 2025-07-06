from django.contrib import admin
from django.urls import path
from .models import Wallet, Transaction
from audit.mixins import ExcelExportMixin


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('user', 'wallet_address', 'balance', 'currency', 'last_updated')
    list_filter = ('currency',)
    search_fields = ('user__email', 'wallet_address')
    actions = ['export_selected_to_excel']

    excel_export_fields = ['user__email', 'wallet_address', 'balance', 'currency', 'last_updated']
    excel_export_filename = 'wallets'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'export-wallets/',
                self.admin_site.admin_view(self.export_all_wallets_excel),
                name='export_wallets_excel'
            ),
        ]
        return custom_urls + urls

    def export_all_wallets_excel(self, request):
        queryset = self.get_queryset(request)
        return self.export_selected_to_excel(request, queryset)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'wallet', 'amount', 'transaction_type', 'status', 'timestamp')
    list_filter = ('status', 'transaction_type', 'timestamp')
    search_fields = ('wallet__wallet_address', 'tx_hash', 'description')
    actions = ['export_selected_to_excel']

    excel_export_fields = [
        'id', 'wallet__wallet_address', 'amount', 'transaction_type',
        'status', 'tx_hash', 'description', 'timestamp'
    ]
    excel_export_filename = 'transactions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'export-transactions/',
                self.admin_site.admin_view(self.export_all_transactions_excel),
                name='export_transactions_excel'
            ),
        ]
        return custom_urls + urls

    def export_all_transactions_excel(self, request):
        queryset = self.get_queryset(request)
        return self.export_selected_to_excel(request, queryset)
