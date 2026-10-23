"""
URLs do app cart.

Prefixo: /carrinho/ (definido em config/urls.py)
"""

from django.urls import path

from .views import cart_add, cart_detail

app_name = 'cart'

urlpatterns = [
    path('', cart_detail, name='cart-detail'),
    path('adicionar/', cart_add, name='cart-add'),
]
