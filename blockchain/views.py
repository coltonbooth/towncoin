from decimal import Decimal, InvalidOperation
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Transaction, Block, Wallet
from .serializers import TransactionSerializer, BlockSerializer


class AddTransactionView(APIView):
    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Extract transaction details
            sender_id = serializer.validated_data['sender']
            recipient_id = serializer.validated_data['recipient']
            amount = serializer.validated_data['amount']

            # Validate sender's balance
            sender_wallet, created = Wallet.objects.get_or_create(user_id=sender_id)
            if sender_wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            # Process the transaction
            recipient_wallet, created = Wallet.objects.get_or_create(user_id=recipient_id)
            sender_wallet.balance -= amount
            recipient_wallet.balance += amount
            sender_wallet.save()
            recipient_wallet.save()

            # Save the transaction
            transaction = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlockchainView(APIView):
    def get(self, request):
        blocks = Block.objects.all()
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)


class AddBlockView(APIView):
    def post(self, request):
        transactions = Transaction.objects.filter(on_chain=False)

        if not transactions:
            return Response({"message": "No pending transactions found"}, status=status.HTTP_400_BAD_REQUEST)

        last_block = Block.objects.last()
        new_block = Block(
            index=last_block.index + 1 if last_block else 0,
            prev_hash=last_block.hash if last_block else '0',
            nonce=0
        )

        new_block._transactions_to_set = transactions
        new_block.save()
        new_block.transactions.set(transactions)
        transactions.update(on_chain=True)

        new_block.save()

        serializer = BlockSerializer(new_block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WalletBalanceView(APIView):
    def get(self, request, wallet_address):
        try:
            wallet = Wallet.objects.get(id=wallet_address)
            balance = wallet.balance
            return Response({'wallet_address': wallet_address, 'balance': balance})
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        

class WalletView(APIView):
    def get(self, request, issuer_id):
        try:
            wallets = Wallet.objects.filter(issuer_id=issuer_id)

            # Retrieve exclude_zero from query parameters and convert to boolean
            exclude_zero = request.query_params.get('exclude_zero', 'false').lower() == 'true'
            only_zero = request.query_params.get('only_zero', 'false').lower() == 'true'

            # Filter wallets by balance
            if exclude_zero:
                wallets = wallets.exclude(balance=0)
            elif only_zero:
                wallets = wallets.filter(balance=0)

            # Prepare the response data
            wallets_data = [{'address': wallet.id, 'balance': wallet.balance} for wallet in wallets]

            return Response(wallets_data)
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)


class TransferView(APIView):
    def post(self, request):
        sender_id = request.data.get('sender')
        recipient_id = request.data.get('recipient')
        amount = request.data.get('amount', 0)
        print(sender_id, recipient_id, amount)
        if sender_id == recipient_id:
            return Response({'error': 'Sender and recipient cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            sender_wallet = Wallet.objects.select_for_update().get(id=sender_id)
            recipient_wallet = Wallet.objects.select_for_update().get(id=recipient_id)

            if sender_wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            # Update wallet balances
            sender_wallet.balance -= amount
            recipient_wallet.balance += amount
            sender_wallet.save()
            recipient_wallet.save()

            # Create and save the transaction
            transaction_data = {
                'sender': sender_id,
                'recipient': recipient_id,
                'amount': amount,
            }
            transaction_serializer = TransactionSerializer(data=transaction_data)
            if transaction_serializer.is_valid():
                transaction_serializer.save()
            else:
                return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Transfer successful', 'transaction': transaction_serializer.data})


@api_view(['POST'])
def register_wallet(request):
    issuer_id = request.data.get('issuer_id')
    if not issuer_id:
        return Response({'error': 'Issuer ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    new_wallet = Wallet.objects.create(issuer_id=issuer_id)
    return Response({'message': 'Wallet created', 'wallet_id': str(new_wallet.id)}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def issue_coins(request):
    wallet_address = request.data.get('wallet_address')
    amount_to_issue = request.data.get('amount')
    issuer_id = request.data.get('issuer_id')

    if not wallet_address or amount_to_issue is None:
        return Response({'error': 'Wallet address and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

    if not check_if_able_to_issue_coins(issuer_id):
        return Response({'error': 'Only authorized accounts can issue coins. This activity has been logged.'}, status=status.HTTP_403_FORBIDDEN)

    wallet, _ = Wallet.objects.get_or_create(id=wallet_address, issuer_id=issuer_id)

    # Create a transaction representing the issuing event
    system_wallet_address = '0xDEADBEEF'
    transaction = Transaction(
        sender=system_wallet_address, 
        recipient=wallet.id, 
        amount=amount_to_issue,
    )
    transaction.save()

    wallet.balance += amount_to_issue
    wallet.save()

    return Response({'message': f'{amount_to_issue} TownCoins issued successfully', 'new_balance': wallet.balance})

def check_if_able_to_issue_coins(issuer_id):
    return False if issuer_id != 'colton2' else True