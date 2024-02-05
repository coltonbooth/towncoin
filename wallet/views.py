import json

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from blockchain.models import Wallet, PaperWallet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from blockchain.models import Transaction


class WalletDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        
        try:
            user_wallet = Wallet.objects.get(user_id=request.user.id)
            context = {
                'wallet_id': user_wallet.id,
                'balance': user_wallet.balance,
                'user_id': request.user.username
            }
            return render(request, 'wallet/dashboard.html', context)
        except Wallet.DoesNotExist:
            return redirect('create_wallet')  # Redirect to wallet creation view
        

@login_required
@csrf_exempt
def make_paper_wallet(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = data.get("amount")

        try:
            amount = Decimal(amount)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid amount format'}, status=400)
        
        user_wallet = Wallet.objects.get(issuer_id=request.user.id)

        if user_wallet.balance >= amount:
            # Create new wallet
            new_wallet = Wallet.objects.create(
                balance=amount,
                # other necessary fields...
            )
            user_wallet.balance -= amount
            user_wallet.save()

            # Create transaction record
            transaction = Transaction(
                sender=user_wallet.id,
                recipient=new_wallet.id,
                amount=amount
            )
            transaction.save()

            PaperWallet.objects.create(
                creator_wallet=user_wallet,
                paper_wallet=new_wallet.id,
            )
            
            return JsonResponse({'new_wallet_id': new_wallet.id})
        
        return JsonResponse({'error': 'Insufficient balance'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
