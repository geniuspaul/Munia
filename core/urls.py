from django.urls import path
from .views import SignUpView, VerifyOTPView, LoginView, LogoutView, CurrentUserView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('api/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', CurrentUserView.as_view(), name='user'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
