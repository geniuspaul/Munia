from django.urls import path
from .views import WalletView, WalletTransferAPIView, TransactionHistoryAPIView

urlpatterns = [
    path('api/wallet/', WalletView.as_view(), name='wallet'),
    path('api/transfer/', WalletTransferAPIView.as_view(), name='wallet-transfer'),
    path('api/transaction-history/', TransactionHistoryAPIView.as_view(), name='transaction-history')
]
