from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Transaction, Profile
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
import requests

# -------------------------
# DASHBOARD VIEW (SAFE, NO IMAGE)
# -------------------------
@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {})

# -------------------------
# SIGNUP VIEW
# -------------------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ensure profile created
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


# -------------------------
# CRYPTO API (ALL COINS)
# -------------------------
@login_required
def crypto_prices_all(request):
    coins = "bitcoin,ethereum,dogecoin,cardano,solana"
    cache_key = "crypto_prices_all"

    data = cache.get(cache_key)
    if not data:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": coins, "vs_currencies": "usd"}
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            cache.set(cache_key, data, 300)
        except requests.exceptions.RequestException as e:
            print(f"CoinGecko request failed: {e}")
            data = {c: {"usd": None} for c in coins.split(",")}

    return JsonResponse(data)


# -------------------------
# CRYPTO HISTORY
# -------------------------
@login_required
def crypto_history(request):
    coin = request.GET.get('id', '').lower()
    if not coin:
        return JsonResponse({'error': 'Missing coin id'}, status=400)

    cache_key = f"hist_{coin}"
    data = cache.get(cache_key)

    if not data:
        try:
            url = f'https://api.coingecko.com/api/v3/coins/{coin}/market_chart'
            params = {'vs_currency': 'usd', 'days': 7, 'interval': 'daily'}
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if 'prices' not in data:
                data = {"prices": []}
            cache.set(cache_key, data, 3600)
        except requests.exceptions.RequestException as e:
            print(f"CoinGecko history request failed for {coin}: {e}")
            data = {"prices": []}

    return JsonResponse(data)