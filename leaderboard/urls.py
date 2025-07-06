from django.urls import path
from .views import TopEarnerAPIView, TopReferralAPIView

urlpatterns = [
    path('api/TopEarner/', TopEarnerAPIView.as_view(), name='TopEarner'),
    path('api/TopReferral/', TopReferralAPIView.as_view(), name='TopReferral'),
    
]
