from django.urls import path

from .views import (
    address_create,
    address_delete,
    address_edit,
    address_list,
    user_login,
    user_logout,
)


app_name = "users"

urlpatterns = [
    path("login/", user_login, name="user-login"),
    path("logout/", user_logout, name="user-logout"),
    path("enderecos/", address_list, name="address-list"),
    path("enderecos/novo/", address_create, name="address-create"),
    path("enderecos/<int:pk>/editar/", address_edit, name="address-edit"),
    path("enderecos/<int:pk>/excluir/", address_delete, name="address-delete"),
]