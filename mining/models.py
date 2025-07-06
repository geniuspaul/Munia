import uuid
from datetime import date
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# --------------------- Mining Session ---------------------

class MiningSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    device_hash = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Session {self.session_id} for {self.user}"


# --------------------- Quiz Models ---------------------

class QuizQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    A = models.CharField(max_length=255)
    B = models.CharField(max_length=255)
    C = models.CharField(max_length=255)
    D = models.CharField(max_length=255)

    CORRECT_OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    correct_option = models.CharField(max_length=10, choices=CORRECT_OPTION_CHOICES)
    reward = models.DecimalField(max_digits=18, decimal_places=8, default=20.00)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:100]


class DailyQuiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(default=date.today, unique=True)
    quiz = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - {self.quiz}"


class QuizSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mining_session = models.ForeignKey(MiningSession, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.id} - {'Correct' if self.is_correct else 'Wrong'}"


# --------------------- Daily Sign-In ---------------------

class DailySignIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mining_session = models.ForeignKey(MiningSession, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_signins')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} signed in on {self.date}"


# --------------------- Social Task ---------------------

class SocialTask(models.Model):
    TASK_TYPES = [
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('comment', 'Comment'),
        ('retweet', 'Retweet'),
        ('subscribe', 'Subscribe'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    url = models.URLField(help_text="Link to the task (e.g. Twitter post)")
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SocialTaskSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mining_session = models.ForeignKey(MiningSession, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(SocialTask, on_delete=models.CASCADE)
    proof = models.URLField(help_text="URL of the proof (e.g. tweet, screenshot, etc.)")
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.task.title}"
