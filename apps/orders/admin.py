"""
Admin do app orders.
"""

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'size', 'quantity', 'unit_price', 'subtotal')

    @admin.display(description='Subtotal')
    def subtotal(self, obj):
        return f'R$ {obj.subtotal:.2f}'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
