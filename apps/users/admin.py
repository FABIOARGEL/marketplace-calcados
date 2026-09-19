"""
Admin do app users.
Registra CustomUser, SellerProfile e Address no painel administrativo do Django.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Address, CustomUser, SellerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin para CustomUser.

    Estende o UserAdmin padrão adicionando o campo user_type.
    O login é feito por e-mail; o username é mantido para compatibilidade
    interna com o AbstractUser e o admin do Django.
    """

    list_display = (
        'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active'
    )
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('email',)

    # Redefine fieldsets para colocar email em destaque
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name')}),
        (_('Tipo de usuário'), {'fields': ('user_type',)}),
        (
            _('Permissões'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'user_type',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    """Admin para SellerProfile."""

    list_display = (
        'store_name', 'user', 'cnpj',
        'shipping_rate_per_km', 'shipping_distance_km',
        'is_active', 'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('store_name', 'user__email', 'cnpj')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'store_name', 'cnpj', 'description', 'is_active')}),
        (
            _('Configuração de Frete (Simulado)'),
            {
                'fields': ('shipping_rate_per_km', 'shipping_distance_km'),
                'description': _(
                    'SIMULAÇÃO: Não há integração com API de mapas. '
                    'A distância é informada pelo vendedor. '
                    'Fórmula: frete = distância_km × valor_por_km.'
                ),
            },
        ),
        (_('Auditoria'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin para endereços de entrega dos usuários."""

    list_display = (
        'user', 'nickname', 'recipient_name',
        'city', 'state', 'zip_code', 'is_default',
    )
    list_filter = ('state', 'is_default')
    search_fields = (
        'user__email', 'recipient_name', 'street', 'city', 'zip_code'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
