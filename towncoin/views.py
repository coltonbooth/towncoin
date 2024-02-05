from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from blockchain.models import Wallet


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a linked wallet for the new user
            Wallet.objects.create(user_id=user.id, issuer_id=user.id, is_linked=True)
            login(request, user)
            return redirect("wallet_dashboard")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('wallet_dashboard')
    form = AuthenticationForm()
    return render(request=request, template_name="registration/login.html", context={"login_form": form})

def logout_request(request):
    logout(request)
    return redirect("login")  # Redirect to the login page
