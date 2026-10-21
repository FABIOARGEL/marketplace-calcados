"""
URLs do app products.

Prefixo: /produtos/ (definido em config/urls.py)
"""

from django.urls import path

from .views import (
    product_create,
    product_edit,
    product_list_seller,
    product_toggle_active,
    seller_product_list,
    seller_product_toggle,
)

app_name = 'products'

urlpatterns = [
    path('novo/', product_create, name='product-create'),
    path('meus-produtos/', seller_product_list, name='seller-product-list'),
    path('meus-produtos/', product_list_seller, name='product-list-seller'),
    path(
        'meus-produtos/<int:pk>/editar/',
        product_edit,
        name='product-edit',
    ),
    path(
        'meus-produtos/<int:pk>/ativar-desativar/',
        product_toggle_active,
        name='product-toggle-active',
    ),
    path(
        'meus-produtos/<int:pk>/toggle/',
        seller_product_toggle,
        name='seller-product-toggle',
    ),
]
