from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('id', 'wallet_address', 'balance', 'last_updated', 'user')
        

class TransferSerializer(serializers.Serializer):
    from_wallet = serializers.CharField()
    to_wallet = serializers.CharField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=8)
    description = serializers.CharField(required=False, allow_blank=True)

