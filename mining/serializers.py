from rest_framework import serializers
from .models import QuizQuestion, DailySignIn, SocialTask, MiningSession


# --------------------- Daily Sign-In ---------------------

class MiningSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiningSession
        fields = '__all__'

class DailySignInSerializer(serializers.ModelSerializer):
    mining_session = MiningSessionSerializer(read_only=True)

    class Meta:
        model = DailySignIn
        fields = ['id', 'user', 'date', 'mining_session']
        read_only_fields = ['id', 'user', 'date', 'mining_session']



# --------------------- Quiz Serializers ---------------------

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question', 'A', 'B', 'C', 'D', 'reward']


class QuizAnswerSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    selected_option = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'])


# --------------------- Social Task Serializers ---------------------

class SocialTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialTask
        fields = '__all__'


class SocialTaskSubmissionSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()
