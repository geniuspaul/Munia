import hashlib
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now, timedelta
from user_agents import parse as parse_user_agent

from core.models import UserProfile
from .models import SuspiciousActivityLog, UserDevice


# 🔐 Helper: Generate device fingerprint
def generate_device_id(request):
    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    ip = request.META.get('REMOTE_ADDR', '')
    base = f"{user_agent_str}:{ip}"
    return hashlib.sha256(base.encode()).hexdigest()


# 🚨 1. Detect suspicious IPs on signup
@receiver(post_save, sender=UserProfile)
def detect_suspicious_signup(sender, instance, created, **kwargs):
    if created:
        same_ip_users = UserProfile.objects.filter(ip_address=instance.ip_address).count()
        if same_ip_users > 5:
            SuspiciousActivityLog.objects.create(
                user=instance.user,
                activity_type="SUSPICIOUS_IP",
                description=f"More than 5 accounts created from IP: {instance.ip_address}"
            )


@receiver(post_save, sender=UserProfile)
def detect_referral_farming(sender, instance, created, **kwargs):
    if not created or not instance.used_referral_code:
        return

    referral_code = instance.used_referral_code
    ip_address = instance.ip_address
    device_info = instance.device_info

    ip_count = UserProfile.objects.filter(
        used_referral_code=referral_code,
        ip_address=ip_address
    ).count()

    device_count = UserProfile.objects.filter(
        used_referral_code=referral_code,
        device_info=device_info
    ).count()

    recent_count = UserProfile.objects.filter(
        used_referral_code=referral_code,
        created_at__gte=now() - timedelta(minutes=10)
    ).count()

    if ip_count > 3 or device_count > 3 or recent_count > 3:
        SuspiciousActivityLog.objects.create(
            user=instance.user,
            activity_type="Referral Farming",
            description=(
                f"Referral Code: {referral_code}, "
                f"IP Matches: {ip_count}, "
                f"Device Matches: {device_count}, "
                f"Recent Signups: {recent_count}"
            )
        )


# 📱 3. Log device info on login
@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse_user_agent(user_agent_str)
    device_id = generate_device_id(request)

    os = user_agent.os.family
    browser = user_agent.browser.family

    # Log device if not already recorded
    device, created = UserDevice.objects.get_or_create(
        user=user,
        device_id=device_id,
        defaults={"os": os, "browser": browser, "is_trusted": False}
    )

    # Detect shared device abuse
    user_count = UserDevice.objects.filter(device_id=device_id).values("user").distinct().count()

    if user_count > 3:
        already_logged = SuspiciousActivityLog.objects.filter(
            activity_type="Shared device across multiple users",
            description__icontains=device_id,
            resolved=False
        ).exists()

        if not already_logged:
            SuspiciousActivityLog.objects.create(
                user=user,
                activity_type="Shared device across multiple users",
                description=(
                    f"Device ID {device_id} used by {user_count} different users. "
                    f"Current user: {user.email}"
                )
            )