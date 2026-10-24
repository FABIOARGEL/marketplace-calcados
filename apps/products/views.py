
"""
Views do app products.

Permite cadastrar, listar, editar e ativar ou desativar produtos.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm, ProductImageFormSet, StockFormSet
from .models import Category, Product


def product_list(request):
    """Catálogo público de calçados com busca, filtros e paginação.

    Parâmetros de query string:
        q:          termo de busca (name ou description, icontains)
        categoria:  slug da categoria
        tamanho:    tamanho do calçado (pode ser múltiplo: ?tamanho=38&tamanho=39)
        marca:      nome da marca (iexact)
        preco_min:  preço mínimo (Decimal)
        preco_max:  preço máximo (Decimal)
        page:       página da paginação
    """
    from .models import Stock

    query = request.GET.get('q', '').strip()
    categoria_slug = request.GET.get('categoria', '').strip()
    tamanhos_sel = request.GET.getlist('tamanho')
    marca_sel = request.GET.get('marca', '').strip()
    preco_min = request.GET.get('preco_min', '').strip()
    preco_max = request.GET.get('preco_max', '').strip()

    qs = (
        Product.objects
        .filter(is_active=True)
        .select_related('category', 'seller')
        .prefetch_related('images')
        .order_by('-created_at')
    )

    # Filtro por texto
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Filtro por categoria (slug)
    if categoria_slug:
        qs = qs.filter(category__slug=categoria_slug)

    # Filtro por tamanho — JOIN com Stock onde quantity > 0
    if tamanhos_sel:
        qs = qs.filter(
            stock_items__size__in=tamanhos_sel,
            stock_items__quantity__gt=0,
        ).distinct()

    # Filtro por marca (case-insensitive)
    if marca_sel:
        qs = qs.filter(brand__iexact=marca_sel)

    # Filtro por faixa de preço
    if preco_min:
        try:
            qs = qs.filter(price__gte=preco_min)
        except Exception:
            pass
    if preco_max:
        try:
            qs = qs.filter(price__lte=preco_max)
        except Exception:
            pass

    total_count = qs.count()

    # --- Opções dinâmicas de filtro (apenas valores existentes no banco) ---
    categories = Category.objects.filter(products__is_active=True).distinct().order_by('name')
    marcas = (
        Product.objects
        .filter(is_active=True)
        .values_list('brand', flat=True)
        .distinct()
        .order_by('brand')
    )
    tamanhos_disponiveis = (
        Stock.objects
        .filter(quantity__gt=0, product__is_active=True)
        .values_list('size', flat=True)
        .distinct()
        .order_by('size')
    )

    # Verifica se há algum filtro ativo (exceto busca por texto)
    filtros_ativos = any([categoria_slug, tamanhos_sel, marca_sel, preco_min, preco_max])

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'products/product_list.html',
        {
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': paginator.num_pages > 1,
            'query': query,
            'total_count': total_count,
            'categories': categories,
            'marcas': marcas,
            'tamanhos_disponiveis': tamanhos_disponiveis,
            # Filtros selecionados (para manter estado na UI)
            'categoria_sel': categoria_slug,
            'tamanhos_sel': tamanhos_sel,
            'marca_sel': marca_sel,
            'preco_min': preco_min,
            'preco_max': preco_max,
            'filtros_ativos': filtros_ativos,
        },
    )


def product_detail(request, pk):
    """Página pública de detalhes de um produto (RF08).

    Exibe imagens, descrição, preços e o formulário de
    "Adicionar ao carrinho" com seleção de tamanho e quantidade.
    Tamanhos sem estoque ficam desabilitados no select.
    """
    produto = get_object_or_404(
        Product.objects
        .select_related('category', 'seller')
        .prefetch_related('images', 'stock_items'),
        pk=pk,
        is_active=True,
    )

    stock_items = produto.stock_items.filter(quantity__gt=0).order_by('size')

    return render(
        request,
        'products/product_detail.html',
        {
            'produto': produto,
            'stock_items': stock_items,
            'has_stock': stock_items.exists(),
        },
    )


@login_required
def product_create(request):
    """Cadastra um produto com imagens e estoque."""
    if not request.user.is_seller:
        messages.error(
            request,
            'Apenas vendedores podem cadastrar produtos.',
        )
        return redirect('home')


    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            prefix='images',
        )
        stock_formset = StockFormSet(request.POST, prefix='stock')

        form_valid = form.is_valid()
        images_valid = image_formset.is_valid()
        stock_valid = stock_formset.is_valid()

        if form_valid and images_valid and stock_valid:
            stock_preenchido = any(
                f.cleaned_data.get('size')
                and not f.cleaned_data.get('DELETE', False)
                for f in stock_formset.forms
                if f.cleaned_data
            )

            if not stock_preenchido:
                messages.error(
                    request,
                    'Informe pelo menos um tamanho no estoque.',
                )
            else:
                produto = form.save(commit=False)
                produto.seller = request.user
                produto.save()

                image_formset.instance = produto
                image_formset.save()

                stock_formset.instance = produto
                stock_formset.save()

                messages.success(
                    request,
                    f'Produto "{produto.name}" cadastrado com sucesso!',
                )
                return redirect('products:seller-product-list')
    else:
        form = ProductForm()
        image_formset = ProductImageFormSet(prefix='images')
        stock_formset = StockFormSet(prefix='stock')

    return render(
        request,
        'products/product_form.html',
        {
            'form': form,
            'image_formset': image_formset,
            'stock_formset': stock_formset,
        },
    )


@login_required
def seller_product_list(request):
    """Lista os produtos do vendedor com paginação."""
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    qs = (
        request.user.products
        .select_related('category')
        .prefetch_related('images', 'stock_items')
        .order_by('-created_at')
    )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'products/seller_product_list.html',
        {
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': paginator.num_pages > 1,
            'active_count': qs.filter(is_active=True).count(),
            'inactive_count': qs.filter(is_active=False).count(),
        },
    )


def product_list_seller(request):
    """Mantém compatibilidade com o nome antigo da listagem."""
    return seller_product_list(request)


@login_required
def product_edit(request, pk):
    """Edita um produto pertencente ao vendedor autenticado."""
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produto = get_object_or_404(
        Product,
        pk=pk,
        seller=request.user,
    )

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=produto)
        image_formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=produto,
            prefix='images',
        )
        stock_formset = StockFormSet(
            request.POST,
            instance=produto,
            prefix='stock',
        )

        form_valid = form.is_valid()
        images_valid = image_formset.is_valid()
        stock_valid = stock_formset.is_valid()

        if form_valid and images_valid and stock_valid:
            stock_preenchido = any(
                f.cleaned_data.get('size')
                and not f.cleaned_data.get('DELETE', False)
                for f in stock_formset.forms
                if f.cleaned_data
            )

            if not stock_preenchido:
                messages.error(
                    request,
                    'Informe pelo menos um tamanho no estoque.',
                )
            else:
                produto = form.save()
                image_formset.instance = produto
                image_formset.save()
                stock_formset.instance = produto
                stock_formset.save()

                messages.success(
                    request,
                    f'Produto "{produto.name}" atualizado com sucesso!',
                )
                return redirect('products:seller-product-list')
    else:
        form = ProductForm(instance=produto)
        image_formset = ProductImageFormSet(
            instance=produto,
            prefix='images',
        )
        stock_formset = StockFormSet(
            instance=produto,
            prefix='stock',
        )

    return render(
        request,
        'products/product_form.html',
        {
            'form': form,
            'image_formset': image_formset,
            'stock_formset': stock_formset,
            'produto': produto,
            'modo_edicao': True,
        },
    )


@login_required
@require_POST
def product_toggle_active(request, pk):
    """Ativa ou desativa um produto sem excluí-lo."""
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produto = get_object_or_404(
        Product,
        pk=pk,
        seller=request.user,
    )

    produto.is_active = not produto.is_active
    produto.save(update_fields=['is_active', 'updated_at'])

    status = 'ativado' if produto.is_active else 'desativado'
    messages.success(
        request,
        f'Produto "{produto.name}" {status} com sucesso.',
    )

    return redirect('products:seller-product-list')


def seller_product_toggle(request, pk):
    """Mantém compatibilidade com a rota de ativação da equipe."""
    return product_toggle_active(request, pk)
