"""
URLs do app orders.

Prefixo: /pedidos/ (definido em config/urls.py)

Rotas:
    checkout/              → checkout              (GET)  — resumo + formulário
    confirmar/             → order_confirm         (POST) — processa pedido
    sucesso/<pk>/          → order_success         (GET)  — página de confirmação
    vendedor/pedidos/      → seller_order_list     (GET)  — dashboard do vendedor
    vendedor/pedidos/<pk>/ → seller_order_detail   (GET/POST) — detalhe + atualização de status
"""

from django.urls import path

from .views import (
    checkout,
    order_confirm,
    order_success,
    seller_order_detail,
    seller_order_list,
)

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('confirmar/', order_confirm, name='order-confirm'),
    path('sucesso/<int:pk>/', order_success, name='order-success'),
    path('vendedor/pedidos/', seller_order_list, name='seller-order-list'),
    path('vendedor/pedidos/<int:pk>/', seller_order_detail, name='seller-order-detail'),
]
