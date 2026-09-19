"""
Modelos do app orders.

Order: pedido realizado pelo cliente (RF15, RF16, RF17, RF18, RF19).
OrderItem: produto incluído em um pedido com preço snapshot.

PAGAMENTO SIMULADO:
    Este sistema NÃO realiza processamento financeiro real.
    Não há integração com Mercado Pago, Stripe, PIX real, cartão real
    ou qualquer gateway de pagamento.
    O pagamento é registrado apenas para fins acadêmicos e de demonstração.
    O campo `payment_status` sempre será marcado como APPROVED após confirmação,
    simulando uma aprovação fictícia.

FRETE SIMULADO:
    O frete é calculado com base na distância configurada pelo vendedor
    (SellerProfile.shipping_distance_km) e na taxa por km
    (SellerProfile.shipping_rate_per_km).
    Não há integração com API de mapas ou geolocalização real nesta versão.
    Fórmula: frete = distância_km × valor_por_km
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product


class Order(models.Model):
    """
    Pedido de compra realizado pelo cliente (RF15, RF16, RF17).

    Campos principais:
        - user: cliente que realizou o pedido.
        - shipping_address: endereço de entrega escolhido no checkout.
        - subtotal: valor dos produtos sem frete.
        - shipping_cost: valor do frete calculado (simulado).
        - total: subtotal + frete.
        - payment_method: método de pagamento escolhido (SIMULADO).
        - payment_status: status do pagamento (SIMULADO — sem processamento real).
        - status: ciclo de vida do pedido.

    IMPORTANTE: O pagamento registrado aqui é apenas uma simulação acadêmica.
    Nenhuma transação financeira real é processada pelo sistema.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Aguardando confirmação')
        CONFIRMED = 'CONFIRMED', _('Confirmado')
        SHIPPED = 'SHIPPED', _('Em trânsito')
        DELIVERED = 'DELIVERED', _('Entregue')
        CANCELLED = 'CANCELLED', _('Cancelado')

    class PaymentMethod(models.TextChoices):
        """
        Métodos de pagamento disponíveis.
        TODOS SÃO SIMULADOS — nenhum processamento financeiro real ocorre.
        """
        CREDIT_CARD_SIM = 'CREDIT_CARD_SIM', _('Cartão de Crédito (Simulado)')
        DEBIT_CARD_SIM = 'DEBIT_CARD_SIM', _('Cartão de Débito (Simulado)')
        PIX_SIM = 'PIX_SIM', _('PIX (Simulado)')
        BOLETO_SIM = 'BOLETO_SIM', _('Boleto Bancário (Simulado)')

    class PaymentStatus(models.TextChoices):
        """
        Status do pagamento simulado.
        ATENÇÃO: Estes status representam apenas uma simulação.
        Nenhum processamento financeiro real é executado.
        """
        PENDING = 'PENDING', _('Pagamento Pendente')
        APPROVED = 'APPROVED', _('Pagamento Aprovado (Simulado)')
        CANCELLED = 'CANCELLED', _('Pagamento Cancelado')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Cliente'),
    )
    shipping_address = models.ForeignKey(
        'users.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Endereço de entrega'),
        help_text=_('Endereço selecionado pelo cliente no checkout.'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Status do pedido'),
    )

    # --- Valores financeiros (snapshot no momento da compra) ---
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Subtotal'),
        help_text=_('Valor dos produtos sem frete, calculado no momento do checkout.'),
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Frete'),
        help_text=_(
            'Valor do frete calculado no checkout. '
            'SIMULADO: baseado na distância configurada pelo vendedor × taxa/km. '
            'Não há integração com API de logística real.'
        ),
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total'),
        help_text=_('Subtotal + frete, calculado no momento da finalização do pedido.'),
    )

    # --- Pagamento simulado ---
    # ATENÇÃO: NÃO há processamento financeiro real. Fins acadêmicos apenas.
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        verbose_name=_('Método de pagamento'),
        help_text=_(
            'SIMULADO — Nenhuma cobrança real é realizada. '
            'Campo para fins acadêmicos e de demonstração.'
        ),
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_('Status do pagamento'),
        help_text=_(
            'SIMULADO — Representa apenas o status fictício do pagamento. '
            'Nenhuma transação financeira real é processada.'
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.pk} — {self.user.email} — {self.get_status_display()}'


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
        """Valor total deste item (preço unitário × quantidade)."""
        return self.unit_price * self.quantity
