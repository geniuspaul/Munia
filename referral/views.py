from datetime import date
from django.db.models import Sum
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Referral
from wallet.models import Transaction
from mining.models import DailySignIn 
from django.contrib.auth import get_user_model

User = get_user_model()

class ReferralListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        now_time = now()
        start_of_month = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get all referrals made by the user
        referrals = Referral.objects.filter(referrer=user).select_related('referred')
        referred_users = [r.referred for r in referrals]

        # Get referred user emails for display
        referred_data = [
            {
                "email": r.referred.email,
                "referral_code": r.referral_code,
                "timestamp": r.timestamp,
            }
            for r in referrals
        ]

        # Get total referral earnings (from transactions)
        total_earned = Transaction.objects.filter(
            wallet__user=user,
            description__icontains='referral',
            transaction_type='receive',
            status='completed',
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Get referral earnings this month
        monthly_earned = Transaction.objects.filter(
            wallet__user=user,
            description__icontains='referral',
            transaction_type='receive',
            status='completed',
            timestamp__gte=start_of_month  # fixed field name here
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Get users who signed in today
        today_signins = DailySignIn.objects.filter(
            user__in=referred_users,
            date=today
        ).values_list('user__email', flat=True)

        return Response({
            "total_referred": referrals.count(),
            "total_earned": str(total_earned),
            "earned_this_month": str(monthly_earned),
            "referred_users": referred_data,
            "referrals_signed_in_today": list(today_signins),
        })
