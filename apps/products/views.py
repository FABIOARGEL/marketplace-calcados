"""
Views do app products.

product_create:
    Permite ao vendedor autenticado cadastrar um novo calçado com
    imagens e estoque por tamanho.

seller_product_list:
    Lista todos os produtos (ativos e inativos) do vendedor logado,
    com paginação de 10 itens por página.

seller_product_toggle:
    Alterna o status is_active do produto (ativar / desativar).
    Operação de soft delete — nunca exclui fisicamente.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm, ProductImageFormSet, StockFormSet
from .models import Product


@login_required
def product_create(request):
    """
    Exibe e processa o formulário de cadastro de produto.

    Acesso restrito a usuários com user_type = SELLER.
    Em caso de usuário não vendedor, redireciona para home com mensagem.

    GET:
        Renderiza formulário em branco com formsets de imagens e estoque.

    POST:
        Valida todos os formulários.
        Exige pelo menos um item de estoque válido (tamanho + quantidade).
        Salva produto associado ao vendedor logado, imagens e estoque.
        Redireciona para lista de produtos do vendedor em caso de sucesso.
        Renderiza novamente com erros em caso de falha.
    """
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
        stock_formset = StockFormSet(
            request.POST,
            prefix='stock',
        )

        # Valida todos os formulários antes de salvar
        form_valid = form.is_valid()
        images_valid = image_formset.is_valid()
        stock_valid = stock_formset.is_valid()

        if form_valid and images_valid and stock_valid:
            # Verifica se há pelo menos um item de estoque preenchido
            stock_preenchido = any(
                f.cleaned_data.get('size') and not f.cleaned_data.get('DELETE', False)
                for f in stock_formset.forms
                if f.cleaned_data
            )

            if not stock_preenchido:
                messages.error(
                    request,
                    'Informe pelo menos um tamanho no estoque.',
                )
            else:
                # Salva o produto sem commit para associar o vendedor
                produto = form.save(commit=False)
                produto.seller = request.user
                produto.save()

                # Salva imagens vinculadas ao produto
                image_formset.instance = produto
                image_formset.save()

                # Salva itens de estoque vinculados ao produto
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

    return render(request, 'products/product_form.html', {
        'form': form,
        'image_formset': image_formset,
        'stock_formset': stock_formset,
    })


@login_required
def seller_product_list(request):
    """
    Lista os produtos do vendedor autenticado com paginação.

    Acesso restrito a vendedores. Redireciona para home se o usuário
    não for vendedor.

    Exibe todos os produtos do vendedor (ativos e inativos), ordenados
    do mais recente para o mais antigo, com 10 itens por página.

    Contexto enviado ao template:
        page_obj  — página atual do Paginator
        paginator — instância do Paginator (total de páginas, etc.)
        is_paginated — bool indicando se há mais de uma página
    """
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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    active_count = qs.filter(is_active=True).count()
    inactive_count = qs.filter(is_active=False).count()

    return render(request, 'products/seller_product_list.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'active_count': active_count,
        'inactive_count': inactive_count,
    })



@login_required
@require_POST
def seller_product_toggle(request, pk):
    """
    Alterna o status is_active de um produto do vendedor.

    Operação de soft delete reversível — nunca exclui o produto do banco.
    Somente o vendedor dono do produto pode executar esta ação.

    POST: inverte is_active e redireciona para a lista de produtos.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produto = get_object_or_404(Product, pk=pk, seller=request.user)
    produto.is_active = not produto.is_active
    produto.save(update_fields=['is_active', 'updated_at'])

    status = 'ativado' if produto.is_active else 'desativado'
    messages.success(request, f'Produto "{produto.name}" {status} com sucesso.')

    return redirect('products:seller-product-list')
