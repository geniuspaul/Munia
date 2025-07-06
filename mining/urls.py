from django.urls import path
from .views import DailyQuizAPIView, SubmitQuizAPIView, DailySignInAPIView, SocialTaskRewardAPIView, SocialTaskAPIView

urlpatterns = [
    path('api/daily-quiz/', DailyQuizAPIView.as_view(), name='daily-quiz'),
    path('api/submit-quiz/', SubmitQuizAPIView.as_view(), name='submit-quiz'),
    path('api/daily-signin/', DailySignInAPIView.as_view(), name='daily-signin'),
    path('api/social-task-reward/', SocialTaskRewardAPIView.as_view(), name='social-task-reward'),
    path('api/social-task/', SocialTaskAPIView.as_view(), name='social-task'),
    
    
]
