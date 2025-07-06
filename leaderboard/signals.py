from django.db.models.signals import post_save
from django.dispatch import receiver
from wallet.models import Wallet
from leaderboard.models import TopEarner, TopReferral
from django.db import transaction
from referral.models import Referral

def update_earning_ranks():
    earners = TopEarner.objects.all().order_by('-total_earnings')
    for i, entry in enumerate(earners, start=1):
        if entry.rank != i:
            entry.rank = i
            entry.save(update_fields=['rank'])

@receiver(post_save, sender=Wallet)
def update_top_earner(sender, instance, **kwargs):
    try:
        user = instance.user
        total_earnings = instance.balance

        entry, _ = TopEarner.objects.get_or_create(user=user)
        entry.total_earnings = total_earnings
        entry.save(update_fields=['total_earnings'])

        transaction.on_commit(update_earning_ranks)

    except Exception as e:
        print(f"🔥 TopEarner signal error: {e}")


def update_referral_ranks():
    referrals = TopReferral.objects.all().order_by('-total_referrals')
    for i, entry in enumerate(referrals, start=1):
        if entry.rank != i:
            entry.rank = i
            entry.save(update_fields=['rank'])

@receiver(post_save, sender=Referral)
def update_top_referral(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        user = instance.referrer
        count = Referral.objects.filter(referrer=user).count()

        entry, _ = TopReferral.objects.get_or_create(user=user)
        entry.total_referrals = count
        entry.save(update_fields=['total_referrals'])

        transaction.on_commit(update_referral_ranks)

    except Exception as e:
        print(f"🔥 TopReferral signal error: {e}")
