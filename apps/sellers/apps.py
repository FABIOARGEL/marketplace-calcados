"""
App sellers — Área do Vendedor (SOLESTEP).
"""

from django.apps import AppConfig


class SellersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sellers"
    verbose_name = "Área do Vendedor"
