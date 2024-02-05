from django.urls import path
from .views import AddTransactionView, AddBlockView, register_wallet, BlockchainView, issue_coins, WalletBalanceView, TransferView, WalletView

urlpatterns = [
    path('add-transaction/', AddTransactionView.as_view(), name='add-transaction'),
    path('add-block/', AddBlockView.as_view(), name='add-block'),
    path('view/', BlockchainView.as_view(), name='blockchain'),
    path('register-wallet/', register_wallet, name='register-wallet'),
    path('issue-coins/', issue_coins, name='issue-coins'),
    path('wallet-balance/<str:wallet_address>/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('all-wallets/<str:issuer_id>/', WalletView.as_view(), name='wallet-view'),
    path('transfer/', TransferView.as_view(), name='transfer'),
]
