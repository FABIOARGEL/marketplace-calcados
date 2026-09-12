"""
App: products
Responsável pelo catálogo de calçados do marketplace.

Entidades:
- Category: categorias dos calçados (ex: Tênis, Sandália, Bota)
- Product: calçado com dados de venda
- ProductImage: imagens do produto
- Stock: controle de estoque por produto e tamanho
"""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Produtos'
