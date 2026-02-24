from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('api/crypto/prices', views.crypto_prices_all, name='crypto_prices_all'),
    path('api/crypto/history', views.crypto_history, name='crypto_history'),
]
