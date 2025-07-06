from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
import random

from django.db import transaction
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from wallet.models import Wallet, Transaction
from .models import (
    QuizQuestion, DailyQuiz, DailySignIn,
    QuizSubmission, SocialTask, SocialTaskSubmission
)
from .serializers import (
    QuizQuestionSerializer, QuizAnswerSerializer,
    DailySignInSerializer, SocialTaskSerializer,
    SocialTaskSubmissionSerializer, MiningSessionSerializer
)
from .utils import get_client_ip, m_session

SIGNIN_REWARD = 10

# ---------------- Daily Sign-In ---------------- #

class DailySignInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        today = date.today()
        mining_session = m_session(request)

        if DailySignIn.objects.filter(user=user, date=today).exists():
            return Response({"message": "Already signed in today."}, status=200)

        try:
            with transaction.atomic():
                signin = DailySignIn.objects.create(user=user, mining_session=mining_session)

                wallet = Wallet.objects.select_for_update().get(user=user)
                wallet.balance += Decimal(SIGNIN_REWARD)
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    amount=SIGNIN_REWARD,
                    transaction_type='receive',
                    status='completed',
                    tx_hash=str(uuid4()),
                    description='Daily sign-in reward'
                )

                serialized_session = MiningSessionSerializer(signin.mining_session)

                return Response({
                    "message": "Sign-in successful. You earned 10 points.",
                    "date": signin.date,
                    "mining_session": serialized_session.data
                })

        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=404)
        except Exception as e:
            return Response({"error": "Sign-in failed.", "details": str(e)}, status=500)

# ---------------- Daily Quiz ---------------- #

class DailyQuizAPIView(APIView):
    def get(self, request):
        today = date.today()

        try:
            daily_quiz = DailyQuiz.objects.get(date=today)
        except DailyQuiz.DoesNotExist:
            quizzes = QuizQuestion.objects.all()
            if not quizzes.exists():
                return Response({"error": "No quiz questions available."}, status=404)

            daily_quiz = DailyQuiz.objects.create(
                date=today,
                quiz=random.choice(quizzes)
            )

        serializer = QuizQuestionSerializer(daily_quiz.quiz)
        return Response(serializer.data)


class SubmitQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quiz_id = serializer.validated_data['quiz_id']
        selected_option = serializer.validated_data['selected_option']
        mining_session = m_session(request)

        try:
            quiz = QuizQuestion.objects.get(id=quiz_id)
        except QuizQuestion.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=404)

        today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        already_submitted = QuizSubmission.objects.filter(
            user=request.user,
            quiz=quiz,
            submitted_at__gte=today_start,
            submitted_at__lt=today_end
        ).exists()

        if already_submitted:
            return Response({"error": "You already submitted this quiz today."}, status=400)

        is_correct = (selected_option == quiz.correct_option)
    
        QuizSubmission.objects.create(
            user=request.user,
            quiz=quiz,
            selected_option=selected_option,
            is_correct=is_correct,
            mining_session=mining_session
        )

        if is_correct:
            try:
                with transaction.atomic():
                    wallet = Wallet.objects.select_for_update().get(user=request.user)
                    wallet.balance += Decimal(quiz.reward)
                    wallet.save()

                    Transaction.objects.create(
                        wallet=wallet,
                        amount=quiz.reward,
                        transaction_type='receive',
                        status='completed',
                        tx_hash=str(uuid4()),
                        description='Quiz reward bonus'
                    )

            except Wallet.DoesNotExist:
                return Response({"error": "Wallet not found."}, status=404)

            return Response({
                "message": "Correct answer! You earned 20 MUN points.",
                "correct": True
            })

        return Response({
            "message": "Incorrect answer.",
            "correct": False
        })


# ---------------- Social Task ---------------- #

class SocialTaskAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            task = SocialTask.objects.get(active=True)
        except SocialTask.DoesNotExist:
            return Response({"error": "No active social task found."}, status=404)

        serializer = SocialTaskSerializer(task)
        return Response(serializer.data)


class SocialTaskRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SocialTaskSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        task_id = serializer.validated_data['task_id']
        mining_session = m_session(request)

        try:
            task = SocialTask.objects.get(id=task_id)
        except SocialTask.DoesNotExist:
            return Response({"error": "Task not found."}, status=404)

        if SocialTaskSubmission.objects.filter(user=request.user, task=task).exists():
            return Response({"error": "Task already completed."}, status=400)

        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(user=request.user)
                wallet.balance += task.reward
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    amount=task.reward,
                    transaction_type='receive',
                    status='completed',
                    tx_hash=str(uuid4()),
                    description=f'Reward for completing task: {task.title}'
                )

                SocialTaskSubmission.objects.create(
                    user=request.user,
                    task=task,
                    mining_session = mining_session
                )

        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=404)

        return Response({
            "message": f"Task '{task.title}' completed successfully! You earned {task.reward} points.",
            "reward": str(task.reward)
        })
