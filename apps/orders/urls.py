"""
URLs do app orders.

Prefixo: /pedidos/ (definido em config/urls.py)

Rotas:
    checkout/                           → checkout                    (GET)  — resumo + formulário
    confirmar/                          → order_confirm               (POST) — processa pedido
    sucesso/<pk>/                       → order_success               (GET)  — página de confirmação
    meus-pedidos/                       → order_list                  (GET)  — histórico do cliente
    meus-pedidos/<pk>/                  → order_detail                (GET)  — detalhe do pedido do cliente
    vendedor/pedidos/                   → seller_order_list           (GET)  — dashboard do vendedor
    vendedor/pedidos/<pk>/              → seller_order_detail         (GET)  — detalhe do pedido (vendedor)
    vendedor/pedidos/<pk>/status/       → seller_order_update_status  (POST) — atualiza status do pedido
"""

from django.urls import path

from .views import (
    checkout,
    order_confirm,
    order_detail,
    order_list,
    order_success,
    seller_order_detail,
    seller_order_list,
    seller_order_update_status,
)

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('confirmar/', order_confirm, name='order-confirm'),
    path('sucesso/<int:pk>/', order_success, name='order-success'),
    path('meus-pedidos/', order_list, name='order-list'),
    path('meus-pedidos/<int:pk>/', order_detail, name='order-detail'),
    path('vendedor/pedidos/', seller_order_list, name='seller-order-list'),
    path('vendedor/pedidos/<int:pk>/', seller_order_detail, name='seller-order-detail'),
    path('vendedor/pedidos/<int:pk>/status/', seller_order_update_status, name='seller-order-update-status'),
]
