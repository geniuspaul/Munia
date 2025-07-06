from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TopEarner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='top_earner_record')
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rank = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_earnings']

    def __str__(self):
        return f"💰 {self.user.email} | #{self.rank} | ${self.total_earnings}"


class TopReferral(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='top_referral_record')
    total_referrals = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_referrals']

    def __str__(self):
        return f"👥 {self.user.email} | #{self.rank} | {self.total_referrals} referrals"
