from smtplib import SMTPException
from django.utils.timezone import now
from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from decimal import Decimal
import uuid
import logging
from datetime import timedelta

from .serializers import SignUpSerializer, VerifyOTPSerializer, CurrentUserSerializer, ResetPasswordSerializer
from core.models import OTP, UserProfile
from wallet.models import Wallet, Transaction
from referral.models import Referral
from mining.models import MiningSession
from .utils import get_client_ip, generate_referral_code, generate_otp, send_otp_email


logger = logging.getLogger(__name__)
User = get_user_model()

MUN_REWARD_AMOUNT = Decimal("100")
REFERRAL_BONUS = Decimal("100")


class SignUpView(APIView):
    def post(self, request):
        
        try:
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "User with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST)
            OTP.objects.filter(email=email).delete()
            otp_code = generate_otp()
            send_otp_email(email, otp_code)
            OTP.objects.create(email=email, code=otp_code, expires_at=now() + timedelta(minutes=5))

            return Response({"message": "We’ve sent a 6-digit code to your email. Please check your inbox."}, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            logger.warning("Validation error: %s", ve)
            return Response({"error": "Invalid input", "details": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        except SMTPException as mail_error:
            logger.warning("Email send failed: %s", mail_error)
            return Response({"error": "We couldn't send the OTP. Please check your email address or try again later."}, status=status.HTTP_502_BAD_GATEWAY)

        except ObjectDoesNotExist as ode:
            logger.warning("Object not found: %s", ode)
            return Response({"error": "Something went wrong while processing your request. Please try again."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.exception("Unexpected error during signup")
            return Response({"error": "Something went wrong on our end. Please try again shortly.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            email = data['email']
            code = data['code']
            password = data['password']
            country = data['country']
            referral_code = data.get('referral_code')
            ip_address = data['ip_address']
            device_info = data['device_info']

            # OTP Validation
            try:
                otp = OTP.objects.get(email=email, code=code)
            except OTP.DoesNotExist:
                return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)

            if otp.expires_at < now():
                otp.delete()
                return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            otp.delete()

            with transaction.atomic():
                tx_hash = uuid.uuid4()
                user = User.objects.create(email=email)
                user.set_password(password)
                user.save()

                profile = UserProfile.objects.create(
                    user=user,
                    country=country,
                    used_referral_code=referral_code or None,
                    ip_address=ip_address,
                    device_info=device_info
                )

                wallet = Wallet.objects.create(user=user)
                wallet.balance += MUN_REWARD_AMOUNT
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    amount=MUN_REWARD_AMOUNT,
                    transaction_type='receive',
                    status='completed',
                    tx_hash=tx_hash,
                    description="Signup reward"
                )

                if referral_code:
                    try:
                        referrer_profile = UserProfile.objects.get(referral_code=referral_code)

                        # Create the referral (no referral_code field anymore)
                        Referral.objects.create(
                            referrer=referrer_profile.user,
                            referred=user
                        )

                        # Reward the referrer
                        referrer_wallet = Wallet.objects.select_for_update().get(user=referrer_profile.user)
                        referrer_wallet.balance += REFERRAL_BONUS
                        referrer_wallet.save()

                        Transaction.objects.create(
                            wallet=referrer_wallet,
                            amount=REFERRAL_BONUS,
                            transaction_type='receive',
                            status='completed',
                            tx_hash=uuid.uuid4(),
                            description=f"Referral bonus"
                        )
                    except (UserProfile.DoesNotExist, Wallet.DoesNotExist):
                        pass  # Ignore silently

                refresh = RefreshToken.for_user(user)

                MiningSession.objects.create(
                    user=user,
                    session_id=str(uuid.uuid4()),
                    start_time=now(),
                    device_hash=device_info,
                    ip_address=ip_address,
                    status='active'
                )

            return Response({
                "message": "OTP verified and user created successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"id": str(user.id), "email": user.email}
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("OTP verification failed")
            return Response({"error": "Something went wrong during OTP verification", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            device_hash = request.data.get('device_hash')

            if not email or not password or not device_hash:
                return Response({'detail': 'Email, password, and device_hash are required'}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, email=email, password=password)
            if user is None:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            MiningSession.objects.create(
                user=user,
                session_id=str(uuid.uuid4()),
                start_time=now(),
                device_hash=device_hash,
                ip_address=get_client_ip(request),
                status='active'
            )

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {'id': str(user.id), 'email': user.email}
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Login failed")
            return Response({'error': 'Something went wrong during login', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            MiningSession.objects.filter(user=request.user, status='active').delete()

            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)

        except TokenError as e:
            logger.exception("Invalid token during logout")
            return Response({"error": "Invalid token", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Logout failed")
            return Response({"error": "Something went wrong during logout", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = CurrentUserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to fetch current user details")
            return Response(
                {"error": "Failed to fetch user details", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            otp = OTP.objects.get(email=email, code=otp_code)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)

        if otp.expires_at < now():
            otp.delete()
            return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            otp.delete()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

def home(request):
    return HttpResponse("MUNIA")
