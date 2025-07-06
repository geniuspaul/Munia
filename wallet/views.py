from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Wallet, Transaction
from django.db import transaction
from decimal import Decimal
from .serializers import WalletSerializer, TransferSerializer
from rest_framework.permissions import IsAuthenticated
from uuid import uuid4
from django.db.models import Sum


class WalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = WalletSerializer(wallet)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)


class WalletTransferAPIView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            from_wallet_address = data['from_wallet']
            to_wallet_address = data['to_wallet']
            amount = Decimal(data['amount'])
            description = data.get('description', '')

            if from_wallet_address == to_wallet_address:
                return Response({"error": "Sender and receiver wallets must be different."}, status=400)

            try:
                with transaction.atomic():
                    sender_wallet = Wallet.objects.select_for_update().get(wallet_address=from_wallet_address)
                    receiver_wallet = Wallet.objects.select_for_update().get(wallet_address=to_wallet_address)

                    if sender_wallet.balance < amount:
                        return Response({"error": "Insufficient balance."}, status=400)

                    # Update balances
                    sender_wallet.balance -= amount
                    sender_wallet.save()

                    receiver_wallet.balance += amount
                    receiver_wallet.save()

                    tx_hash = str(uuid4())

                    # Create send transaction (from sender to receiver)
                    Transaction.objects.create(
                        wallet=sender_wallet,
                        tx_wallet=receiver_wallet,
                        amount=amount,
                        transaction_type='send',
                        status='completed',
                        tx_hash=tx_hash,
                        description=description or f"Sent to {to_wallet_address[:10]}..."
                    )

                    # Create receive transaction (from receiver from sender)
                    Transaction.objects.create(
                        wallet=receiver_wallet,
                        tx_wallet=sender_wallet,
                        amount=amount,
                        transaction_type='receive',
                        status='completed',
                        tx_hash=tx_hash,
                        description=description or f"Received from {from_wallet_address[:10]}..."
                    )

                    return Response({
                        "message": "Transfer successful.",
                        "tx_hash": tx_hash
                    }, status=status.HTTP_200_OK)

            except Wallet.DoesNotExist:
                return Response({"error": "One or both wallets not found."}, status=404)
            except Exception as e:
                return Response({"error": "Something went wrong.", "details": str(e)}, status=500)

        return Response(serializer.errors, status=400)
    


class TransactionHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=404)

        transactions = Transaction.objects.filter(wallet=wallet).order_by('-timestamp')

        total_sent = transactions.filter(transaction_type='send').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_received = transactions.filter(transaction_type='receive').aggregate(
            total=Sum('amount')
        )['total'] or 0

        tx_data = [
            {
                "amount": str(tx.amount),
                "type": tx.transaction_type,
                "status": tx.status,
                "description": tx.description,
                "tx_hash": tx.tx_hash,
                "date": tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for tx in transactions
        ]

        return Response({
            "total_sent": str(total_sent),
            "total_received": str(total_received),
            "transactions": tx_data
        })
