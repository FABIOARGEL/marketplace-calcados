"""
URLs do app products.

Prefixo: /produtos/ (definido em config/urls.py)
"""

from django.urls import path

from .views import product_create, seller_product_list, seller_product_toggle

app_name = 'products'

urlpatterns = [
    path('novo/', product_create, name='product-create'),
    path('meus-produtos/', seller_product_list, name='seller-product-list'),
    path('meus-produtos/<int:pk>/toggle/', seller_product_toggle, name='seller-product-toggle'),
]
