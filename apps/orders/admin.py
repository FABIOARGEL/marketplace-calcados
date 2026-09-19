"""
Admin do app orders.

NOTA: O pagamento exibido aqui é SIMULADO.
Não há processamento financeiro real no sistema.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_subtotal',)
    fields = ('product', 'size', 'quantity', 'unit_price', 'item_subtotal')

    @admin.display(description='Subtotal')
    def item_subtotal(self, obj):
        return f'R$ {obj.subtotal:.2f}'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status',
        'subtotal', 'shipping_cost', 'total',
        'payment_method', 'payment_status',
        'created_at',
    )
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('user__email', 'id')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'shipping_address')
    inlines = [OrderItemInline]
    fieldsets = (
        (_('Dados do pedido'), {
            'fields': ('user', 'status', 'shipping_address'),
        }),
        (_('Valores'), {
            'fields': ('subtotal', 'shipping_cost', 'total'),
        }),
        (
            _('Pagamento (SIMULADO — sem processamento financeiro real)'),
            {
                'fields': ('payment_method', 'payment_status'),
                'description': _(
                    'ATENÇÃO: O pagamento é apenas simulado para fins acadêmicos. '
                    'Nenhuma cobrança real é realizada.'
                ),
            },
        ),
        (_('Auditoria'), {'fields': ('created_at', 'updated_at')}),
    )
