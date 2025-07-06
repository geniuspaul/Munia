from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class SuspiciousActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    os = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)
    last_used = models.DateTimeField(auto_now=True)
    is_trusted = models.BooleanField(default=False)