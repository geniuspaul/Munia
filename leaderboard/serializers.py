# leaderboard/serializers.py
from rest_framework import serializers
from .models import TopEarner, TopReferral

class TopEarnerSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TopEarner
        fields = [
            'user_email',
            'total_earnings',
            'rank',
            'last_updated',
        ]

class TopReferralSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TopReferral
        fields = [
            'user_email',
            'total_referrals',
            'rank',
            'last_updated',
        ]
