"""
Admin do app cart.
"""

from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'size', 'quantity', 'subtotal')

    @admin.display(description='Subtotal')
    def subtotal(self, obj):
        return f'R$ {obj.subtotal:.2f}'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    inlines = [CartItemInline]
