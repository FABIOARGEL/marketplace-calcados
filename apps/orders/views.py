"""
Views do app orders.

checkout: Primeira etapa do fluxo de compra (RF15).
    - Exige autenticação (@login_required)
    - Redireciona se carrinho vazio
    - Lista endereços do usuário, pré-seleciona o padrão
    - Calcula frete por vendedor (SellerProfile.calculate_shipping)
    - Apresenta subtotal, frete discriminado por vendedor e total
    - Métodos de pagamento simulados (PAGAMENTO SIMULADO — sem cobrança real)

order_confirm: Processa a confirmação do pedido (RF16, RF17, RF18, RF19).
    - Exige autenticação e método POST
    - Valida endereço e método de pagamento
    - Verifica estoque dentro de transaction.atomic() (evitar race condition)
    - Cria Order e OrderItems com snapshot de preço
    - Desconta estoque (Stock.quantity -= CartItem.quantity)
    - Limpa carrinho após confirmação
    - Redireciona para order_success

order_success: Exibe a página de confirmação do pedido.
    - Exige autenticação
    - Apresenta detalhes do Order criado (itens, valores, endereço, pagamento)

order_list: Histórico de pedidos do cliente.
    - Exige autenticação (@login_required)
    - Lista apenas pedidos do usuário logado, ordenados por data decrescente
    - Paginação de 10 por página

order_detail: Detalhe de um pedido do cliente.
    - Exige autenticação (@login_required)
    - get_object_or_404(Order, pk=pk, user=request.user) — garante posse
    - Exibe itens, subtotal, frete, total, endereço, pagamento e status

seller_order_list: Dashboard do vendedor — lista de pedidos com seus itens.
    - Exige autenticação e que o usuário seja SELLER
    - Busca OrderItems onde product__seller == request.user
    - Agrupa por Order, exibindo apenas os itens do vendedor logado
    - Filtro por status e paginação

seller_order_detail: Detalhe de um pedido específico do ponto de vista do vendedor.
    - Exige autenticação e que o usuário seja SELLER
    - Exibe apenas os itens do vendedor naquele pedido
    - Exibe dados do comprador e endereço de entrega
    - Passa next_statuses ao template (apenas transições válidas)

seller_order_update_status: Atualiza o status de um pedido (POST-only).
    - Exige autenticação, SELLER e que o pedido contenha itens do vendedor
    - Valida a transição de status segundo ciclo definido:
        PENDING → CONFIRMED → SHIPPED → DELIVERED
        QUALQUER → CANCELLED
        Voltas de status são rejeitadas
    - Salva o novo status e redireciona com mensagem de sucesso
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.cart.models import Cart
from apps.products.models import Stock
from apps.users.models import Address

from .models import Order, OrderItem


@login_required
def checkout(request):
    """Exibe a página de checkout com resumo do carrinho, seleção de endereço
    e cálculo de frete simulado por vendedor.

    Fórmula de frete (por vendedor):
        frete_vendedor = shipping_distance_km × shipping_rate_per_km

    O frete total é a soma dos fretes de cada vendedor distinto no carrinho.
    """
    # ── Carrinho ──────────────────────────────────────────────────────────────
    try:
        cart = Cart.objects.prefetch_related(
            'items',
            'items__product',
            'items__product__seller',
            'items__product__seller__seller_profile',
            'items__product__images',
        ).get(user=request.user)
    except Cart.DoesNotExist:
        return redirect('cart:cart-detail')

    items = list(cart.items.select_related(
        'product',
        'product__seller',
        'product__seller__seller_profile',
    ).prefetch_related('product__images').order_by('added_at'))

    if not items:
        return redirect('cart:cart-detail')

    # ── Subtotal ──────────────────────────────────────────────────────────────
    subtotal = sum(item.subtotal for item in items)

    # ── Frete por vendedor ────────────────────────────────────────────────────
    # Agrupa itens por vendedor e calcula 1 frete por loja
    sellers_seen: dict = {}  # seller_id → {'profile': ..., 'shipping': Decimal}
    for item in items:
        seller = item.product.seller
        if seller.pk not in sellers_seen:
            try:
                profile = seller.seller_profile
                shipping = profile.calculate_shipping()
            except Exception:
                shipping = Decimal('0.00')
                profile = None
            sellers_seen[seller.pk] = {
                'seller': seller,
                'profile': profile,
                'shipping': shipping,
            }

    shipping_breakdown = list(sellers_seen.values())  # lista para o template
    total_shipping = sum(s['shipping'] for s in shipping_breakdown)

    # ── Total ─────────────────────────────────────────────────────────────────
    total = subtotal + total_shipping

    # ── Endereços ─────────────────────────────────────────────────────────────
    addresses = list(request.user.addresses.order_by('-is_default', '-created_at'))
    default_address = next((a for a in addresses if a.is_default), None)
    preselected_id = default_address.pk if default_address else (
        addresses[0].pk if addresses else None
    )

    # ── Métodos de pagamento ───────────────────────────────────────────────────
    payment_methods = Order.PaymentMethod.choices  # lista de (value, label)

    context = {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'shipping_breakdown': shipping_breakdown,
        'total_shipping': total_shipping,
        'total': total,
        'addresses': addresses,
        'preselected_id': preselected_id,
        'payment_methods': payment_methods,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_POST
def order_confirm(request):
    """Processa a confirmação do pedido (RF16–RF19).

    Fluxo dentro de transaction.atomic():
        1. Valida address_id e payment_method do POST
        2. Carrega o carrinho e verifica se está vazio
        3. Verifica estoque de cada item (race condition protection)
        4. Calcula subtotal e frete
        5. Cria Order com snapshot dos valores
        6. Cria OrderItem para cada CartItem (unit_price = snapshot)
        7. Desconta estoque (Stock.quantity -= CartItem.quantity)
        8. Deleta todos os CartItems (limpa o carrinho)
        9. Redireciona para order-success

    Em caso de erro, transaction.atomic() faz rollback automático.
    O pagamento é SIMULADO — payment_status é sempre marcado como APPROVED.
    """
    # ── Validação de campos POST ───────────────────────────────────────────────
    address_id = request.POST.get('address_id', '').strip()
    payment_method = request.POST.get('payment_method', '').strip()

    if not address_id:
        messages.error(request, 'Selecione um endereço de entrega antes de continuar.')
        return redirect('orders:checkout')

    if not payment_method:
        messages.error(request, 'Selecione uma forma de pagamento antes de continuar.')
        return redirect('orders:checkout')

    # Valida se payment_method é um valor válido do enum
    metodos_validos = [choice[0] for choice in Order.PaymentMethod.choices]
    if payment_method not in metodos_validos:
        messages.error(request, 'Forma de pagamento inválida.')
        return redirect('orders:checkout')

    # Valida endereço (deve pertencer ao usuário autenticado)
    address = get_object_or_404(Address, pk=address_id, user=request.user)

    # ── Carrinho ──────────────────────────────────────────────────────────────
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart:cart-detail')

    items = list(
        cart.items.select_related(
            'product',
            'product__seller',
            'product__seller__seller_profile',
        ).order_by('added_at')
    )

    if not items:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart:cart-detail')

    # ── Processamento atômico ─────────────────────────────────────────────────
    try:
        with transaction.atomic():
            # 1. Verificar estoque de cada item (select_for_update evita race)
            for item in items:
                try:
                    estoque = Stock.objects.select_for_update().get(
                        product=item.product,
                        size=item.size,
                    )
                except Stock.DoesNotExist:
                    raise ValueError(
                        f'Tamanho {item.size} de "{item.product.name}" não está '
                        f'mais disponível.'
                    )

                if estoque.quantity < item.quantity:
                    raise ValueError(
                        f'Estoque insuficiente para "{item.product.name}" '
                        f'(Tam. {item.size}). '
                        f'Disponível: {estoque.quantity} — Solicitado: {item.quantity}.'
                    )

            # 2. Calcular subtotal
            subtotal = sum(item.subtotal for item in items)

            # 3. Calcular frete por vendedor
            sellers_seen: dict = {}
            for item in items:
                seller = item.product.seller
                if seller.pk not in sellers_seen:
                    try:
                        shipping = seller.seller_profile.calculate_shipping()
                    except Exception:
                        shipping = Decimal('0.00')
                    sellers_seen[seller.pk] = shipping

            shipping_cost = sum(sellers_seen.values())
            total = subtotal + shipping_cost

            # 4. Criar Order
            order = Order.objects.create(
                user=request.user,
                shipping_address=address,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total=total,
                payment_method=payment_method,
                payment_status=Order.PaymentStatus.APPROVED,
                status=Order.Status.CONFIRMED,
            )

            # 5. Criar OrderItems com snapshot de preço e descontar estoque
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    quantity=item.quantity,
                    unit_price=item.product.price,  # snapshot do preço atual
                )

                # Desconta estoque
                Stock.objects.filter(
                    product=item.product,
                    size=item.size,
                ).update(quantity=F('quantity') - item.quantity)

            # 6. Limpar carrinho
            cart.items.all().delete()

    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect('orders:checkout')
    except Exception:
        messages.error(
            request,
            'Ocorreu um erro ao processar seu pedido. Tente novamente.',
        )
        return redirect('orders:checkout')

    return redirect('orders:order-success', pk=order.pk)


@login_required
def order_success(request, pk):
    """Exibe a página de confirmação do pedido (RF19).

    Recupera o Order pelo pk verificando que pertence ao usuário autenticado.
    Passa ao template todos os detalhes: itens, valores, endereço e pagamento.
    """
    order = get_object_or_404(
        Order.objects.select_related(
            'shipping_address',
        ).prefetch_related(
            'items',
            'items__product',
            'items__product__images',
        ),
        pk=pk,
        user=request.user,
    )

    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list(request):
    """Histórico de pedidos do cliente autenticado.

    Lista apenas os pedidos do usuário logado, ordenados do mais recente
    para o mais antigo. Paginação de 10 itens por página.
    """
    orders_qs = (
        Order.objects
        .filter(user=request.user)
        .select_related('shipping_address')
        .prefetch_related('items')
        .order_by('-created_at')
    )

    paginator = Paginator(orders_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'total_orders': paginator.count,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, pk):
    """Detalhe de um pedido do cliente autenticado.

    Usa get_object_or_404 com filtro user=request.user para garantir que
    apenas o dono do pedido consiga visualizá-lo. Retorna 404 para pedidos
    de outros usuários, evitando vazamento de dados.
    """
    order = get_object_or_404(
        Order.objects.select_related(
            'shipping_address',
        ).prefetch_related(
            'items',
            'items__product',
            'items__product__images',
        ),
        pk=pk,
        user=request.user,
    )

    context = {
        'order': order,
        'status_choices': Order.Status.choices,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def seller_order_list(request):
    """Dashboard do vendedor: lista pedidos que contêm produtos do vendedor logado.

    Apenas usuários com user_type == SELLER podem acessar.
    Agrupa os OrderItems por Order, calculando o subtotal dos itens do vendedor.
    Suporta filtro por status via query param ?status= e paginação.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    # Filtro por status
    status_filter = request.GET.get('status', '').strip().upper()
    status_choices = Order.Status.choices

    # Buscar OrderItems do vendedor logado
    items_qs = (
        OrderItem.objects
        .filter(product__seller=request.user)
        .select_related(
            'order',
            'order__user',
            'order__shipping_address',
            'product',
        )
        .order_by('-order__created_at')
    )

    if status_filter and status_filter in dict(Order.Status.choices):
        items_qs = items_qs.filter(order__status=status_filter)

    # Agrupar por Order, mantendo apenas os itens do vendedor
    orders_dict: dict = {}
    for item in items_qs:
        order = item.order
        if order.pk not in orders_dict:
            orders_dict[order.pk] = {
                'order': order,
                'items': [],
                'seller_subtotal': Decimal('0.00'),
            }
        orders_dict[order.pk]['items'].append(item)
        orders_dict[order.pk]['seller_subtotal'] += item.subtotal

    orders_list = list(orders_dict.values())

    # Paginação
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'total_orders': len(orders_list),
    }
    return render(request, 'sellers/order_list.html', context)


# ---------------------------------------------------------------------------
# Tabela de transições válidas de status
# ---------------------------------------------------------------------------

#: Mapeamento de status atual → lista de status para os quais é permitido avançar.
#: Regras:
#:   - O ciclo linear é: PENDING → CONFIRMED → SHIPPED → DELIVERED
#:   - CANCELLED é permitido a partir de qualquer status (exceto DELIVERED)
#:   - Retroceder status é proibido
STATUS_TRANSITIONS: dict[str, list[str]] = {
    Order.Status.PENDING: [
        Order.Status.CONFIRMED,
        Order.Status.CANCELLED,
    ],
    Order.Status.CONFIRMED: [
        Order.Status.SHIPPED,
        Order.Status.CANCELLED,
    ],
    Order.Status.SHIPPED: [
        Order.Status.DELIVERED,
        Order.Status.CANCELLED,
    ],
    Order.Status.DELIVERED: [],   # estado final — sem transições
    Order.Status.CANCELLED: [],   # estado final — sem transições
}


def _obter_proximos_status(status_atual: str) -> list[tuple[str, str]]:
    """Retorna lista de (value, label) dos status para os quais é possível avançar.

    Args:
        status_atual: Valor do status atual do pedido (ex: 'PENDING').

    Returns:
        Lista de tuplas (value, label) com os próximos status válidos.
    """
    proximos_valores = STATUS_TRANSITIONS.get(status_atual, [])
    status_display = dict(Order.Status.choices)
    return [(v, status_display[v]) for v in proximos_valores]


@login_required
def seller_order_detail(request, pk):
    """Detalhe de um pedido do ponto de vista do vendedor (somente GET).

    Apenas usuários com user_type == SELLER podem acessar.
    Exibe apenas os itens do vendedor naquele pedido.
    Passa next_statuses ao template para exibir somente os próximos
    status válidos conforme o ciclo de transições.
    A atualização de status é feita via seller_order_update_status.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    # Verificar que o pedido contém ao menos um produto do vendedor
    order = get_object_or_404(Order, pk=pk)

    seller_items = (
        OrderItem.objects
        .filter(order=order, product__seller=request.user)
        .select_related('product')
        .prefetch_related('product__images')
    )

    if not seller_items.exists():
        messages.error(request, 'Este pedido não contém produtos seus.')
        return redirect('orders:seller-order-list')

    seller_subtotal = sum(item.subtotal for item in seller_items)
    next_statuses = _obter_proximos_status(order.status)

    context = {
        'order': order,
        'seller_items': seller_items,
        'seller_subtotal': seller_subtotal,
        'status_choices': Order.Status.choices,
        'next_statuses': next_statuses,
    }
    return render(request, 'sellers/order_detail.html', context)


@login_required
@require_POST
def seller_order_update_status(request, pk):
    """Atualiza o status de um pedido via POST (apenas vendedores autorizados).

    Validações realizadas (ordem de execução):
        1. Usuário é SELLER
        2. O pedido existe
        3. O pedido contém ao menos um item do vendedor logado
        4. O novo status é um valor válido do enum Order.Status
        5. A transição do status atual para o novo status é permitida
           conforme STATUS_TRANSITIONS (sem pular etapas, sem voltar)

    Em caso de sucesso, salva o novo status e exibe mensagem de sucesso.
    Em qualquer erro, exibe mensagem de erro e redireciona para o detalhe.

    Args:
        pk: Chave primária do pedido a ser atualizado.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    # Garantir que o vendedor tem itens neste pedido
    tem_itens = OrderItem.objects.filter(
        order=order,
        product__seller=request.user,
    ).exists()

    if not tem_itens:
        messages.error(request, 'Este pedido não contém produtos seus.')
        return redirect('orders:seller-order-list')

    novo_status = request.POST.get('status', '').strip().upper()

    # Validar que o novo status é um valor reconhecido pelo enum
    status_validos = {s[0] for s in Order.Status.choices}
    if novo_status not in status_validos:
        messages.error(request, 'Status inválido.')
        return redirect('orders:seller-order-detail', pk=pk)

    # Validar que a transição é permitida
    transicoes_permitidas = STATUS_TRANSITIONS.get(order.status, [])
    if novo_status not in transicoes_permitidas:
        if novo_status == order.status:
            messages.error(request, 'O pedido já está neste status.')
        else:
            messages.error(
                request,
                f'Transição de "{order.get_status_display()}" para '
                f'"{dict(Order.Status.choices)[novo_status]}" não é permitida.',
            )
        return redirect('orders:seller-order-detail', pk=pk)

    # Atualizar status
    order.status = novo_status
    order.save(update_fields=['status', 'updated_at'])

    messages.success(
        request,
        f'Status do pedido #{pk} atualizado para "{order.get_status_display()}".'
    )
    return redirect('orders:seller-order-detail', pk=pk)
