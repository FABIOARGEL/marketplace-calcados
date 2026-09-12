"""
Admin do app products.
"""

from django.contrib import admin

from .models import Category, Product, ProductImage, Stock


class ProductImageInline(admin.TabularInline):
    """Imagens exibidas inline na edição do produto."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


class StockInline(admin.TabularInline):
    """Estoque exibido inline na edição do produto."""
    model = Stock
    extra = 1
    fields = ('size', 'quantity')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'seller', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'brand')
    search_fields = ('name', 'description', 'brand')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, StockInline]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'quantity', 'updated_at')
    list_filter = ('size',)
    search_fields = ('product__name',)
