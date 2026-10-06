"""
URLs do app users.

Prefixo: /usuarios/ (definido em config/urls.py)
"""

from django.urls import path

from .views import (
    address_create,
    address_delete,
    address_edit,
    address_list,
    profile,
    register,
    user_login,
    user_logout,
)


app_name = "users"

urlpatterns = [
    path("login/", user_login, name="user-login"),
    path("logout/", user_logout, name="user-logout"),
    path("cadastro/", register, name="user-register"),
    path("perfil/", profile, name="user-profile"),
    # Endereços de entrega
    path("enderecos/", address_list, name="address-list"),
    path("enderecos/novo/", address_create, name="address-create"),
    path("enderecos/<int:pk>/editar/", address_edit, name="address-edit"),
    path("enderecos/<int:pk>/excluir/", address_delete, name="address-delete"),
]