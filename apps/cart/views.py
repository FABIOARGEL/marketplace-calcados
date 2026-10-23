"""
Views do app cart.

Gerencia as operações do carrinho de compras:
- Adicionar item (criando ou atualizando quantidade)
- Visualizar o carrinho
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.products.models import Product, Stock

from .models import Cart, CartItem


@login_required
@require_POST
def cart_add(request):
    """Adiciona um produto ao carrinho do usuário autenticado.

    Fluxo:
        1. Valida os dados do POST (product_id, size, quantity)
        2. Verifica se o produto está ativo e o tamanho existe no estoque
        3. Verifica se há estoque suficiente
        4. Busca ou cria o Cart do usuário (1 por usuário)
        5. Se CartItem (cart + product + size) já existe: incrementa qty
           Se não existe: cria novo CartItem
        6. Redireciona com mensagem de sucesso ou erro

    Regra de negócio:
        unique_together = ('cart', 'product', 'size') é respeitada via
        get_or_create — nunca há duplicata, só atualização de quantidade.
    """
    product_id = request.POST.get('product_id')
    size = request.POST.get('size', '').strip()
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    # --- Validações básicas ---
    if not product_id or not size or quantity < 1:
        messages.error(request, 'Dados inválidos. Selecione tamanho e quantidade.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    produto = get_object_or_404(Product, pk=product_id, is_active=True)

    # --- Verifica se o tamanho existe e tem estoque ---
    try:
        estoque = Stock.objects.get(product=produto, size=size)
    except Stock.DoesNotExist:
        messages.error(request, f'Tamanho {size} não disponível para "{produto.name}".')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    if estoque.quantity < quantity:
        if estoque.quantity == 0:
            messages.error(
                request,
                f'Tamanho {size} de "{produto.name}" está esgotado.',
            )
        else:
            messages.error(
                request,
                f'Estoque insuficiente. Disponível: {estoque.quantity} unidade(s) no tamanho {size}.',
            )
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # --- Busca ou cria o carrinho do usuário ---
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # --- Respeita unique_together: incrementa se já existe ---
    item, criado = CartItem.objects.get_or_create(
        cart=cart,
        product=produto,
        size=size,
        defaults={'quantity': quantity},
    )

    if not criado:
        nova_quantidade = item.quantity + quantity
        # Valida estoque para a quantidade acumulada
        if estoque.quantity < nova_quantidade:
            messages.warning(
                request,
                f'Você já tem {item.quantity} no carrinho. '
                f'Estoque disponível: {estoque.quantity} unidade(s).',
            )
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        item.quantity = nova_quantidade
        item.save(update_fields=['quantity'])
        messages.success(
            request,
            f'Quantidade de "{produto.name}" (Tam. {size}) atualizada para {item.quantity}.',
        )
    else:
        messages.success(
            request,
            f'"{produto.name}" (Tam. {size}) adicionado ao carrinho!',
        )

    return redirect('cart:cart-detail')


@login_required
def cart_detail(request):
    """Exibe o carrinho de compras do usuário autenticado."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = (
        cart.items
        .select_related('product', 'product__category')
        .prefetch_related('product__images')
        .order_by('added_at')
    )

    return render(
        request,
        'cart/cart_detail.html',
        {
            'cart': cart,
            'items': items,
            'total': cart.total,
        },
    )
