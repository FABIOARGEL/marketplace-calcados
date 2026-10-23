"""
Views do app orders.

checkout: Primeira etapa do fluxo de compra (RF15).
    - Exige autenticação (@login_required)
    - Redireciona se carrinho vazio
    - Lista endereços do usuário, pré-seleciona o padrão
    - Calcula frete por vendedor (SellerProfile.calculate_shipping)
    - Apresenta subtotal, frete discriminado por vendedor e total
    - Métodos de pagamento simulados (PAGAMENTO SIMULADO — sem cobrança real)
"""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.cart.models import Cart
from apps.users.models import Address

from .models import Order


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
