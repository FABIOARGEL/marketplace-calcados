"""
URLs do app cart.

Prefixo: /carrinho/ (definido em config/urls.py)
"""

from django.urls import path

from .views import cart_add, cart_detail, cart_remove, cart_update

app_name = 'cart'

urlpatterns = [
    path('', cart_detail, name='cart-detail'),
    path('adicionar/', cart_add, name='cart-add'),
    path('atualizar/<int:item_pk>/', cart_update, name='cart-update'),
    path('remover/<int:item_pk>/', cart_remove, name='cart-remove'),
]
