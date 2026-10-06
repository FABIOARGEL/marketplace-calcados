"""
Views do app products.

product_create:
    Permite ao vendedor autenticado cadastrar um novo calçado com
    imagens e estoque por tamanho.

product_list_seller:
    Lista os produtos do vendedor logado (placeholder para Sprint futura).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProductForm, ProductImageFormSet, StockFormSet


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
                return redirect('products:product-list-seller')

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
def product_list_seller(request):
    """
    Lista os produtos do vendedor autenticado.

    Acesso restrito a vendedores.
    Exibe apenas os produtos (ativos e inativos) do próprio vendedor.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produtos = (
        request.user.products
        .select_related('category')
        .prefetch_related('images', 'stock_items')
        .order_by('-created_at')
    )

    return render(request, 'products/product_list_seller.html', {
        'produtos': produtos,
    })
