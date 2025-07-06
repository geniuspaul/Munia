from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()
class Referral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(User, related_name='referrals', on_delete=models.CASCADE)
    referred = models.OneToOneField(User, related_name='referred_by', on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.email} referred {self.referred.email} with code {self.referral_code}"
