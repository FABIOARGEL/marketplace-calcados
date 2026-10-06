from django.urls import path

from .views import (
    address_create,
    address_delete,
    address_edit,
    address_list,
)


app_name = "users"

urlpatterns = [
    path("enderecos/", address_list, name="address-list"),
    path("enderecos/novo/", address_create, name="address-create"),
    path("enderecos/<int:pk>/editar/", address_edit, name="address-edit"),
    path("enderecos/<int:pk>/excluir/", address_delete, name="address-delete"),
]