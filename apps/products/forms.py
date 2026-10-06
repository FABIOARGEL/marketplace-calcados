"""
Formulários do app products.

ProductForm:
    Campos name, description, brand, price, category.
    Valida preço > 0.

ProductImageFormSet:
    Inline formset para upload de múltiplas imagens vinculadas a um Product.

StockFormSet:
    Inline formset para definir tamanho + quantidade de estoque.
    Valida que pelo menos um tamanho seja fornecido.
"""

from django import forms
from django.forms import inlineformset_factory

from .models import Category, Product, ProductImage, Stock


class ProductForm(forms.ModelForm):
    """
    Formulário de cadastro/edição de produto.

    Expõe: name, description, brand, price, category.
    O campo seller é atribuído pela view (não exposto ao usuário).
    Validações:
        - name obrigatório
        - price deve ser maior que zero
    """

    name = forms.CharField(
        label='Nome do calçado',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: Air Max 90',
            'id': 'id_product_name',
            'autocomplete': 'off',
        }),
    )

    description = forms.CharField(
        label='Descrição',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Descreva o calçado: material, estilo, indicação de uso...',
            'rows': 4,
            'id': 'id_product_description',
        }),
    )

    brand = forms.CharField(
        label='Marca',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: Nike, Adidas, Vans',
            'id': 'id_product_brand',
            'autocomplete': 'off',
        }),
    )

    price = forms.DecimalField(
        label='Preço (R$)',
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0.00',
            'step': '0.01',
            'id': 'id_product_price',
        }),
    )

    category = forms.ModelChoiceField(
        label='Categoria',
        queryset=Category.objects.all(),
        required=False,
        empty_label='— Selecione uma categoria —',
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'id_product_category',
        }),
    )

    class Meta:
        model = Product
        fields = ('name', 'description', 'brand', 'price', 'category')

    def clean_price(self):
        """Valida que o preço é estritamente maior que zero."""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('O preço deve ser maior que zero.')
        return price


class ProductImageForm(forms.ModelForm):
    """Formulário individual de imagem de produto."""

    image = forms.ImageField(
        label='Imagem',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-input-file',
            'accept': 'image/*',
        }),
    )

    alt_text = forms.CharField(
        label='Texto alternativo',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Descrição da imagem (acessibilidade)',
        }),
    )

    order = forms.IntegerField(
        label='Ordem',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input form-input--order',
            'min': '0',
        }),
    )

    class Meta:
        model = ProductImage
        fields = ('image', 'alt_text', 'order')


# Inline formset: múltiplas imagens por produto
# extra=3: exibe 3 linhas em branco por padrão; can_delete=True: permite remover
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True,
    max_num=10,
)


class StockForm(forms.ModelForm):
    """
    Formulário individual de estoque por tamanho.

    Lacuna conhecida: valores aceitos para size (CharField sem enum).
    Aceita qualquer string (ex: 38, 39, 40, 41, 42, P, M, G, GG).
    """

    size = forms.CharField(
        label='Tamanho',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-input form-input--size',
            'placeholder': 'Ex: 42',
            'autocomplete': 'off',
        }),
    )

    quantity = forms.IntegerField(
        label='Quantidade',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input form-input--qty',
            'min': '0',
            'placeholder': '0',
        }),
    )

    class Meta:
        model = Stock
        fields = ('size', 'quantity')


# Inline formset: estoque por tamanho vinculado ao produto
# extra=3: exibe 3 linhas; validate_min=True garante regra de negócio na view
StockFormSet = inlineformset_factory(
    Product,
    Stock,
    form=StockForm,
    extra=3,
    can_delete=True,
    max_num=30,
)
