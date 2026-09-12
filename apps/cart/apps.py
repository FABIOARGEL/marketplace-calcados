"""
App: cart
Responsável pelo carrinho de compras do cliente.

Entidades:
- Cart: carrinho associado a um usuário
- CartItem: item dentro do carrinho (produto + tamanho + quantidade)
"""

from django.apps import AppConfig


class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cart'
    verbose_name = 'Carrinho'
