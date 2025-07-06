from django.urls import path
from .views import ReferralListAPIView

urlpatterns = [
    path('api/referrals/', ReferralListAPIView.as_view(), name='referrals'),
]