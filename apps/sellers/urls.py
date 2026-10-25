"""
URLs do app sellers — Área do Vendedor.

Prefixo: /painel/ (definido em config/urls.py)

Rotas:
    /painel/                          → dashboard               — Visão geral
    /painel/pedidos/                  → seller_order_list       — Listagem de pedidos
    /painel/pedidos/<pk>/             → seller_order_detail     — Detalhe do pedido
    /painel/produtos/                 → seller_product_list     — Listagem de produtos
    /painel/produtos/novo/            → seller_product_create   — Cadastro de produto
    /painel/produtos/<pk>/editar/     → seller_product_edit     — Edição de produto
    /painel/produtos/<pk>/toggle/     → seller_product_toggle   — Ativar/desativar
    /painel/estoque/                  → inventory               — Controle de estoque
    /painel/estoque/<pk>/<size>/      → inventory_update        — Atualizar qtd estoque
    /painel/vendas/                   → sales                   — Relatórios de vendas
    /painel/loja/                     → store                   — Minha loja
    /painel/configuracoes/            → settings                — Perfil e config.
"""

from django.urls import path

from .views import (
    dashboard,
    inventory,
    inventory_update,
    sales,
    seller_order_detail,
    seller_order_list,
    seller_product_create,
    seller_product_edit,
    seller_product_list,
    seller_product_toggle,
    settings,
    store,
)

app_name = 'sellers'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('pedidos/', seller_order_list, name='order-list'),
    path('pedidos/<int:pk>/', seller_order_detail, name='order-detail'),
    path('produtos/', seller_product_list, name='product-list'),
    path('produtos/novo/', seller_product_create, name='product-create'),
    path('produtos/<int:pk>/editar/', seller_product_edit, name='product-edit'),
    path('produtos/<int:pk>/toggle/', seller_product_toggle, name='product-toggle'),
    path('estoque/', inventory, name='inventory'),
    path('estoque/<int:product_pk>/<str:size>/', inventory_update, name='inventory-update'),
    path('vendas/', sales, name='sales'),
    path('loja/', store, name='store'),
    path('configuracoes/', settings, name='settings'),
]
