"""
App: users
Responsável pelo gerenciamento de usuários do marketplace.

Entidades:
- CustomUser: usuário base com distinção entre cliente e vendedor
- SellerProfile: dados adicionais do perfil do vendedor
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Usuários'
