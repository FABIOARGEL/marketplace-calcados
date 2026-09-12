"""
Modelos do app orders.

Order: pedido realizado pelo cliente (RF15, RF16, RF17, RF18, RF19).
OrderItem: produto incluído em um pedido com preço snapshot.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product


class Order(models.Model):
    """
    Pedido de compra realizado pelo cliente (RF15, RF16, RF17).

    O campo `total` armazena o valor calculado no momento da compra.
    O campo `status` permite rastrear o ciclo de vida do pedido (RF19).
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Aguardando confirmação')
        CONFIRMED = 'CONFIRMED', _('Confirmado')
        SHIPPED = 'SHIPPED', _('Em trânsito')
        DELIVERED = 'DELIVERED', _('Entregue')
        CANCELLED = 'CANCELLED', _('Cancelado')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Cliente'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Status'),
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total'),
        help_text=_('Valor total calculado no momento da finalização do pedido.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.pk} — {self.user.username} — {self.get_status_display()}'


class OrderItem(models.Model):
    """
    Item dentro de um pedido (RF16).

    O preço unitário é armazenado como snapshot no momento da compra,
    garantindo que alterações futuras no produto não afetem pedidos anteriores.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Pedido'),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name=_('Produto'),
    )
    size = models.CharField(
        max_length=10,
        verbose_name=_('Tamanho'),
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Quantidade'),
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Preço unitário'),
        help_text=_('Preço no momento da compra (snapshot).'),
    )

    class Meta:
        verbose_name = _('Item do pedido')
        verbose_name_plural = _('Itens do pedido')

    def __str__(self):
        product_name = self.product.name if self.product else '[produto removido]'
        return f'{self.quantity}x {product_name} (Tam. {self.size}) — R$ {self.unit_price}'

    @property
    def subtotal(self):
        """Valor total deste item."""
        return self.unit_price * self.quantity
