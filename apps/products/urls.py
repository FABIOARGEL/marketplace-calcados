"""
URLs do app products.

Prefixo: /produtos/ (definido em config/urls.py)
"""

from django.urls import path

from .views import product_create, product_list_seller

app_name = 'products'

urlpatterns = [
    path('novo/', product_create, name='product-create'),
    path('meus-produtos/', product_list_seller, name='product-list-seller'),
]
