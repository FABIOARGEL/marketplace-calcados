"""
URLs do app orders.

Prefixo: /pedidos/ (definido em config/urls.py)
"""

from django.urls import path

from .views import checkout

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
]
