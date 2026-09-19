"""
Modelos do app cart.

Cart: carrinho de compras de um usuário autenticado.
CartItem: cada item dentro do carrinho (RF11, RF12, RF13, RF14).
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product


class Cart(models.Model):
    """
    Carrinho de compras.

    Cada usuário possui no máximo um carrinho ativo.
    O carrinho é criado automaticamente quando o usuário adiciona
    o primeiro item (será implementado nas sprints seguintes).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_('Usuário'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Carrinho')
        verbose_name_plural = _('Carrinhos')

    def __str__(self):
        return f'Carrinho de {self.user.email}'

    @property
    def total(self):
        """Calcula o valor total do carrinho (RF14)."""
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """
    Item dentro do carrinho de compras (RF11, RF12, RF13).

    Registra qual produto, em qual tamanho e em qual quantidade
    o usuário deseja comprar.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Carrinho'),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_('Produto'),
    )
    size = models.CharField(
        max_length=10,
        verbose_name=_('Tamanho'),
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Quantidade'),
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Adicionado em'))

    class Meta:
        verbose_name = _('Item do carrinho')
        verbose_name_plural = _('Itens do carrinho')
        # Evita duplicidade do mesmo produto+tamanho no mesmo carrinho
        unique_together = [('cart', 'product', 'size')]

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Tam. {self.size})'

    @property
    def subtotal(self):
        """Valor total deste item (preço × quantidade)."""
        return self.product.price * self.quantity
