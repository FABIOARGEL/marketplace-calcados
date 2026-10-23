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
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
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
