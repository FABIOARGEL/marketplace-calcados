"""
URLs do app orders.

Prefixo: /pedidos/ (definido em config/urls.py)

Rotas:
    checkout/   → checkout        (GET)  — resumo + formulário
    confirmar/  → order_confirm   (POST) — processa pedido
    sucesso/<pk>/ → order_success (GET)  — página de confirmação
"""

from django.urls import path

from .views import checkout, order_confirm, order_success

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('confirmar/', order_confirm, name='order-confirm'),
    path('sucesso/<int:pk>/', order_success, name='order-success'),
]
