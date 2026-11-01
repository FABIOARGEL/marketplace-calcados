"""
Views centrais do projeto (Página inicial / Catálogo de produtos).
"""

from apps.products.views import product_list


def home(request):
    """
    Página inicial do marketplace — Catálogo de produtos.
    """
    return product_list(request)

