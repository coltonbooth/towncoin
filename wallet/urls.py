from django.urls import path
from .views import WalletDashboardView, make_paper_wallet

urlpatterns = [
    path('dashboard/', WalletDashboardView.as_view(), name='wallet_dashboard'),
    path('make-paper/', make_paper_wallet, name='make_paper_wallet'),
]