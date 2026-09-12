"""
Modelos do app users.

CustomUser:
    Extende AbstractUser do Django adicionando o campo `user_type`.
    Distingue entre CLIENTE e VENDEDOR no nível do modelo de usuário.
    Deve ser o AUTH_USER_MODEL antes da primeira migration.

SellerProfile:
    Armazena dados extras do vendedor (nome da loja, CNPJ, descrição).
    Criado automaticamente via signal quando user_type = SELLER.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Usuário customizado do marketplace.

    Herda todos os campos padrão do AbstractUser (username, email,
    password, first_name, last_name, is_active, etc.) e adiciona
    o campo `user_type` para distinguir clientes de vendedores.
    """

    class UserType(models.TextChoices):
        CLIENT = 'CLIENT', _('Cliente')
        SELLER = 'SELLER', _('Vendedor')

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        verbose_name=_('Tipo de usuário'),
        help_text=_('Define se o usuário é um cliente ou vendedor.'),
    )

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['username']

    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'

    @property
    def is_seller(self):
        """Retorna True se o usuário for um vendedor."""
        return self.user_type == self.UserType.SELLER

    @property
    def is_client(self):
        """Retorna True se o usuário for um cliente."""
        return self.user_type == self.UserType.CLIENT


class SellerProfile(models.Model):
    """
    Perfil estendido do vendedor.

    Relacionamento 1:1 com CustomUser.
    Armazena dados específicos do vendedor que não pertencem ao usuário base.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='seller_profile',
        verbose_name=_('Usuário'),
        limit_choices_to={'user_type': CustomUser.UserType.SELLER},
    )
    store_name = models.CharField(
        max_length=150,
        verbose_name=_('Nome da loja'),
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        verbose_name=_('CNPJ'),
        help_text=_('Formato: XX.XXX.XXX/XXXX-XX'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descrição da loja'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criado em'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizado em'),
    )

    class Meta:
        verbose_name = _('Perfil do vendedor')
        verbose_name_plural = _('Perfis dos vendedores')
        ordering = ['store_name']

    def __str__(self):
        return self.store_name
