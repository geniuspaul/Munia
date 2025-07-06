import random
import string
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

def generate_referral_code(length=8):
    from core.models import UserProfile
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code



def generate_otp():
    """Generates a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, code):
    """Sends an OTP email to the given address."""
    subject = 'Your OTP Code'
    message = f'Your One-Time Password (OTP) is: {code}\n\nThis OTP will expire in 5 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL  # Uses configured email in settings.py
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
