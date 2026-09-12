"""
App: orders
Responsável pelo registro e acompanhamento de pedidos.

Entidades:
- Order: pedido realizado pelo cliente
- OrderItem: item dentro de um pedido
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Pedidos'
