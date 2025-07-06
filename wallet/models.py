import uuid
from django.db import models
from django.conf import settings
from wallet.utils import generate_wallet_address  

from django.core.exceptions import ObjectDoesNotExist


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=255, unique=True, default=generate_wallet_address)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    currency = models.CharField(max_length=10, default='MUN')
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.wallet_address}"
    
def get_admin_wallet():
    try:
        return Wallet.objects.get(wallet_address='MUN-ADMIN')
    except ObjectDoesNotExist:
        return None

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    TRANSACTION_TYPES = [
        ('send', 'Send'),
        ('receive', 'Receive'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    tx_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='related_transactions', default=get_admin_wallet)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True, null=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


