"""
Modelos do app products.

Category: categorias de calçados (Tênis, Sandália, Bota, etc.)
Product: calçado disponível para venda no marketplace
ProductImage: imagens associadas a um produto
Stock: quantidade disponível de um produto por tamanho
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Categoria de calçados.
    Permite organizar e filtrar produtos no catálogo (RF07).
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome'),
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('Slug'),
        help_text=_('Identificador amigável para URL (gerado automaticamente).'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descrição'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Calçado disponível para venda (RF04, RF05, RF08, RF09, RF10).

    Cada produto pertence a um vendedor e a uma categoria.
    O campo `is_active` permite desativar sem excluir (RF10).
    """

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Vendedor'),
        limit_choices_to={'user_type': 'SELLER'},
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Categoria'),
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Nome'),
    )
    description = models.TextField(
        verbose_name=_('Descrição'),
    )
    brand = models.CharField(
        max_length=100,
        verbose_name=_('Marca'),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Preço'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Ativo'),
        help_text=_('Desmarque para remover o produto do catálogo sem excluí-lo.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.brand}'


class ProductImage(models.Model):
    """
    Imagem de um produto (RF05).
    Um produto pode ter múltiplas imagens.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Produto'),
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name=_('Imagem'),
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Texto alternativo'),
        help_text=_('Descrição da imagem para acessibilidade.'),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Ordem'),
        help_text=_('Ordena as imagens na exibição (menor = primeiro).'),
    )

    class Meta:
        verbose_name = _('Imagem do produto')
        verbose_name_plural = _('Imagens dos produtos')
        ordering = ['order']

    def __str__(self):
        return f'Imagem {self.order} — {self.product.name}'


class Stock(models.Model):
    """
    Estoque de um produto por tamanho (RF20).

    Cada linha representa a quantidade disponível de um calçado
    em um determinado tamanho (ex: Product='Nike Air Max', size=42, quantity=5).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_items',
        verbose_name=_('Produto'),
    )
    size = models.CharField(
        max_length=10,
        verbose_name=_('Tamanho'),
        help_text=_('Ex: 38, 39, 40, 41, 42'),
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Quantidade'),
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Estoque')
        verbose_name_plural = _('Estoques')
        # Garante que não existam duas linhas para o mesmo produto + tamanho
        unique_together = [('product', 'size')]
        ordering = ['product', 'size']

    def __str__(self):
        return f'{self.product.name} | Tam. {self.size} | Qtd: {self.quantity}'
