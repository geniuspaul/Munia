from rest_framework import serializers
from wallet.serializers import WalletSerializer


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    country = serializers.CharField()
    referral_code = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.IPAddressField()
    device_info = serializers.CharField()

from rest_framework import serializers
from core.models import User, UserProfile
from wallet.models import Wallet
from mining.models import MiningSession
from referral.models import Referral

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'country',
            'referral_code',
            'used_referral_code',
            'ip_address',
            'device_info',
            'created_at'
        ]

class MiningSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiningSession
        fields = ['session_id', 'start_time', 'end_time', 'device_hash', 'ip_address', 'status']

class ReferralSerializer(serializers.ModelSerializer):
    referred_email = serializers.EmailField(source='referred.email', read_only=True)

    class Meta:
        model = Referral
        fields = ['referral_code', 'referred_email', 'created_at']

class CurrentUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile')
    wallet = WalletSerializer(read_only=True)
    mining_sessions = MiningSessionSerializer(source='miningsession_set', many=True, read_only=True)
    referrals = ReferralSerializer(source='referrer_referrals', many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'profile',
            'wallet',
            'mining_sessions',
            'referrals',
            'date_joined',
            'last_login',
        ]

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)