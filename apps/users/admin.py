"""
Admin do app users.
Registra CustomUser e SellerProfile no painel administrativo do Django.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, SellerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin para CustomUser.
    Estende o UserAdmin padrão adicionando o campo user_type.
    """

    # Adiciona user_type à listagem e aos fieldsets
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        (_('Tipo de usuário'), {'fields': ('user_type',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Tipo de usuário'), {'fields': ('user_type',)}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    """Admin para SellerProfile."""

    list_display = ('store_name', 'user', 'cnpj', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('store_name', 'user__username', 'cnpj')
    readonly_fields = ('created_at', 'updated_at')
