"""
Views do painel do vendedor (Área do Vendedor — SOLESTEP).

Módulos:
    dashboard:           Visão geral com KPIs, gráficos e alertas.
    seller_order_list:   Listagem de pedidos (já em orders/views.py — redireciona).
    seller_inventory:    Controle de estoque por produto e tamanho.
    seller_sales:        Relatórios e gráficos de vendas.
    seller_store:        Gerenciamento das informações da loja.
    seller_settings:     Perfil e configurações da conta.
    seller_product_list: Listagem de produtos (wrapper do products/views.py).
    seller_product_create: Cadastro de produto (wrapper).
    seller_product_edit:   Edição de produto (wrapper).
    seller_stock_update:   Atualização de estoque via POST.

Segurança:
    - Todas as views verificam request.user.is_seller.
    - Nenhuma lógica de negócio depende só do frontend.
    - CSRF obrigatório em todos os POSTs.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.orders.models import Order, OrderItem
from apps.products.forms import ProductForm, ProductImageFormSet, StockFormSet
from apps.products.models import Category, Product, Stock
from apps.users.forms import SellerProfileForm, UserProfileForm
from apps.users.models import SellerProfile


# ---------------------------------------------------------------------------
# Decorador auxiliar — garante que o usuário é vendedor
# ---------------------------------------------------------------------------

def _require_seller(view_func):
    """Decorator que verifica autenticação + is_seller antes de entrar na view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:user-login')
        if not request.user.is_seller:
            messages.error(request, 'Acesso restrito a vendedores.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ---------------------------------------------------------------------------
# Dashboard — Visão Geral
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    """
    Painel principal do vendedor com indicadores reais do banco de dados.

    KPIs calculados exclusivamente para o vendedor autenticado:
        - Total de vendas (R$)
        - Qtd. de pedidos com seus produtos
        - Pedidos por status
        - Produtos cadastrados (ativos/inativos)
        - Produtos com estoque baixo (< 5 unid.)
        - Produtos sem estoque

    Seções:
        - Gráfico de pedidos nos últimos 30 dias
        - Top 5 produtos mais vendidos
        - Distribuição de pedidos por status
        - Últimos 5 pedidos
        - Alertas de estoque baixo
        - Atalhos rápidos
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    # ── Produtos do vendedor ─────────────────────────────────────────────────
    produtos_qs = request.user.products.all()
    total_produtos = produtos_qs.count()
    produtos_ativos = produtos_qs.filter(is_active=True).count()
    produtos_inativos = total_produtos - produtos_ativos

    # Estoque baixo: produto com algum size com quantity < 5 mas > 0
    LOW_STOCK_THRESHOLD = 5
    produtos_estoque_baixo = (
        Stock.objects
        .filter(product__seller=request.user, quantity__gt=0, quantity__lt=LOW_STOCK_THRESHOLD)
        .select_related('product')
        .order_by('quantity')[:10]
    )
    count_estoque_baixo = (
        produtos_qs
        .filter(stock_items__quantity__gt=0, stock_items__quantity__lt=LOW_STOCK_THRESHOLD)
        .distinct()
        .count()
    )
    produtos_sem_estoque = (
        produtos_qs
        .filter(is_active=True)
        .exclude(stock_items__quantity__gt=0)
        .count()
    )

    # ── OrderItems do vendedor ────────────────────────────────────────────────
    items_qs = OrderItem.objects.filter(product__seller=request.user)

    # Pedidos únicos com produtos do vendedor
    order_ids = items_qs.values_list('order_id', flat=True).distinct()
    orders_qs = Order.objects.filter(pk__in=order_ids)

    total_pedidos = orders_qs.count()
    pedidos_aguardando = orders_qs.filter(status=Order.Status.PENDING).count()
    pedidos_confirmados = orders_qs.filter(status=Order.Status.CONFIRMED).count()
    pedidos_enviados = orders_qs.filter(status=Order.Status.SHIPPED).count()
    pedidos_entregues = orders_qs.filter(status=Order.Status.DELIVERED).count()
    pedidos_cancelados = orders_qs.filter(status=Order.Status.CANCELLED).count()

    # Total de vendas (soma dos subtotais dos itens do vendedor em pedidos entregues ou enviados)
    total_vendas = items_qs.filter(
        order__status__in=[Order.Status.DELIVERED, Order.Status.SHIPPED, Order.Status.CONFIRMED]
    ).aggregate(
        total=Sum('unit_price')
    )['total'] or Decimal('0.00')

    # Total real: unit_price * quantity
    total_vendas_real = Decimal('0.00')
    for item in items_qs.filter(
        order__status__in=[Order.Status.DELIVERED, Order.Status.SHIPPED, Order.Status.CONFIRMED]
    ).select_related():
        total_vendas_real += item.unit_price * item.quantity

    # Ticket médio
    ticket_medio = (total_vendas_real / total_pedidos) if total_pedidos > 0 else Decimal('0.00')

    # ── Últimos 5 pedidos ────────────────────────────────────────────────────
    ultimos_pedidos = []
    seen = set()
    for item in (
        items_qs
        .select_related('order', 'order__user')
        .order_by('-order__created_at')[:50]
    ):
        if item.order_id not in seen:
            seen.add(item.order_id)
            ultimos_pedidos.append(item.order)
            if len(ultimos_pedidos) >= 5:
                break

    # ── Top 5 produtos mais vendidos ─────────────────────────────────────────
    top_produtos = (
        items_qs
        .values('product__id', 'product__name', 'product__brand')
        .annotate(total_qty=Sum('quantity'), total_revenue=Sum('unit_price'))
        .order_by('-total_qty')[:5]
    )

    # ── Gráfico: pedidos por dia nos últimos 30 dias ──────────────────────────
    hoje = date.today()
    trinta_dias_atras = hoje - timedelta(days=29)

    pedidos_por_dia_raw = (
        Order.objects
        .filter(pk__in=order_ids, created_at__date__gte=trinta_dias_atras)
        .annotate(dia=TruncDate('created_at'))
        .values('dia')
        .annotate(count=Count('id'))
        .order_by('dia')
    )

    dias_map = {row['dia']: row['count'] for row in pedidos_por_dia_raw}
    grafico_pedidos = []
    for i in range(30):
        dia = trinta_dias_atras + timedelta(days=i)
        grafico_pedidos.append({
            'dia': dia.strftime('%d/%m'),
            'count': dias_map.get(dia, 0),
        })

    max_pedidos_dia = max((d['count'] for d in grafico_pedidos), default=1) or 1

    # ── Distribuição por status (para gráfico) ────────────────────────────────
    total_para_pct = total_pedidos or 1
    status_dist = [
        {'label': 'Aguardando', 'count': pedidos_aguardando, 'color': 'var(--color-warning)', 'pct': round(pedidos_aguardando * 100 / total_para_pct)},
        {'label': 'Confirmado', 'count': pedidos_confirmados, 'color': 'var(--color-info)', 'pct': round(pedidos_confirmados * 100 / total_para_pct)},
        {'label': 'Em trânsito', 'count': pedidos_enviados, 'color': 'var(--color-accent)', 'pct': round(pedidos_enviados * 100 / total_para_pct)},
        {'label': 'Entregue', 'count': pedidos_entregues, 'color': 'var(--color-success)', 'pct': round(pedidos_entregues * 100 / total_para_pct)},
        {'label': 'Cancelado', 'count': pedidos_cancelados, 'color': 'var(--color-error)', 'pct': round(pedidos_cancelados * 100 / total_para_pct)},
    ]

    context = {
        # KPIs
        'total_vendas': total_vendas_real,
        'total_pedidos': total_pedidos,
        'pedidos_aguardando': pedidos_aguardando,
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_enviados': pedidos_enviados,
        'pedidos_entregues': pedidos_entregues,
        'pedidos_cancelados': pedidos_cancelados,
        'ticket_medio': ticket_medio,
        # Produtos
        'total_produtos': total_produtos,
        'produtos_ativos': produtos_ativos,
        'produtos_inativos': produtos_inativos,
        'count_estoque_baixo': count_estoque_baixo,
        'produtos_sem_estoque': produtos_sem_estoque,
        # Gráficos
        'grafico_pedidos': grafico_pedidos,
        'max_pedidos_dia': max_pedidos_dia,
        'status_dist': status_dist,
        # Listas
        'ultimos_pedidos': ultimos_pedidos,
        'top_produtos': top_produtos,
        'alertas_estoque': produtos_estoque_baixo,
        'LOW_STOCK_THRESHOLD': LOW_STOCK_THRESHOLD,
    }
    return render(request, 'sellers/dashboard.html', context)


# ---------------------------------------------------------------------------
# Gerenciamento de pedidos — wrapper das views do orders/
# ---------------------------------------------------------------------------

@login_required
def seller_order_list(request):
    """
    Lista pedidos que contêm produtos do vendedor logado.
    Implementação completa no painel com sidebar.
    """
    from decimal import Decimal
    from django.core.paginator import Paginator
    from apps.orders.models import Order, OrderItem

    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    status_filter = request.GET.get('status', '').strip().upper()
    status_choices = Order.Status.choices

    items_qs = (
        OrderItem.objects
        .filter(product__seller=request.user)
        .select_related('order', 'order__user', 'order__shipping_address', 'product')
        .order_by('-order__created_at')
    )

    if status_filter and status_filter in dict(Order.Status.choices):
        items_qs = items_qs.filter(order__status=status_filter)

    orders_dict = {}
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

    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sellers/orders.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'total_orders': len(orders_list),
    })


@login_required
def seller_order_detail(request, pk):
    """
    Detalhe de um pedido do ponto de vista do vendedor.
    Usa o template do painel com sidebar.
    """
    from apps.orders.models import Order, OrderItem
    from apps.orders.views import STATUS_TRANSITIONS, _obter_proximos_status

    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)

    seller_items = (
        OrderItem.objects
        .filter(order=order, product__seller=request.user)
        .select_related('product')
        .prefetch_related('product__images')
    )

    if not seller_items.exists():
        messages.error(request, 'Este pedido não contém produtos seus.')
        return redirect('sellers:order-list')

    seller_subtotal = sum(item.subtotal for item in seller_items)
    next_statuses = _obter_proximos_status(order.status)

    return render(request, 'sellers/order_detail_panel.html', {
        'order': order,
        'seller_items': seller_items,
        'seller_subtotal': seller_subtotal,
        'status_choices': Order.Status.choices,
        'next_statuses': next_statuses,
    })


# ---------------------------------------------------------------------------
# Gerenciamento de produtos — wrappers das views do products/
# ---------------------------------------------------------------------------

@login_required
def seller_product_list(request):
    """Lista os produtos do vendedor no novo layout do painel."""
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    status_filter = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    qs = (
        request.user.products
        .select_related('category')
        .prefetch_related('images', 'stock_items')
        .order_by('-created_at')
    )

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(brand__icontains=q))

    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'inactive':
        qs = qs.filter(is_active=False)

    total_ativos = request.user.products.filter(is_active=True).count()
    total_inativos = request.user.products.filter(is_active=False).count()

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'sellers/products.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
        'status_filter': status_filter,
        'q': q,
    })


@login_required
def seller_product_create(request):
    """Cadastra um produto com imagens e estoque — usa layout do painel."""
    if not request.user.is_seller:
        messages.error(request, 'Apenas vendedores podem cadastrar produtos.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')
        stock_formset = StockFormSet(request.POST, prefix='stock')

        form_valid = form.is_valid()
        images_valid = image_formset.is_valid()
        stock_valid = stock_formset.is_valid()

        if form_valid and images_valid and stock_valid:
            stock_preenchido = any(
                f.cleaned_data.get('size') and not f.cleaned_data.get('DELETE', False)
                for f in stock_formset.forms
                if f.cleaned_data
            )
            if not stock_preenchido:
                messages.error(request, 'Informe pelo menos um tamanho no estoque.')
            else:
                produto = form.save(commit=False)
                produto.seller = request.user
                produto.save()
                image_formset.instance = produto
                image_formset.save()
                stock_formset.instance = produto
                stock_formset.save()
                messages.success(request, f'Produto "{produto.name}" cadastrado com sucesso!')
                return redirect('sellers:product-list')
    else:
        form = ProductForm()
        image_formset = ProductImageFormSet(prefix='images')
        stock_formset = StockFormSet(prefix='stock')

    return render(request, 'sellers/product_form.html', {
        'form': form,
        'image_formset': image_formset,
        'stock_formset': stock_formset,
        'modo_edicao': False,
    })


@login_required
def seller_product_edit(request, pk):
    """Edita um produto pertencente ao vendedor autenticado."""
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produto = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=produto)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=produto, prefix='images')
        stock_formset = StockFormSet(request.POST, instance=produto, prefix='stock')

        form_valid = form.is_valid()
        images_valid = image_formset.is_valid()
        stock_valid = stock_formset.is_valid()

        if form_valid and images_valid and stock_valid:
            stock_preenchido = any(
                f.cleaned_data.get('size') and not f.cleaned_data.get('DELETE', False)
                for f in stock_formset.forms
                if f.cleaned_data
            )
            if not stock_preenchido:
                messages.error(request, 'Informe pelo menos um tamanho no estoque.')
            else:
                produto = form.save()
                image_formset.instance = produto
                image_formset.save()
                stock_formset.instance = produto
                stock_formset.save()
                messages.success(request, f'Produto "{produto.name}" atualizado com sucesso!')
                return redirect('sellers:product-list')
    else:
        form = ProductForm(instance=produto)
        image_formset = ProductImageFormSet(instance=produto, prefix='images')
        stock_formset = StockFormSet(instance=produto, prefix='stock')

    return render(request, 'sellers/product_form.html', {
        'form': form,
        'image_formset': image_formset,
        'stock_formset': stock_formset,
        'produto': produto,
        'modo_edicao': True,
    })


@login_required
@require_POST
def seller_product_toggle(request, pk):
    """Ativa ou desativa um produto sem excluí-lo."""
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produto = get_object_or_404(Product, pk=pk, seller=request.user)
    produto.is_active = not produto.is_active
    produto.save(update_fields=['is_active', 'updated_at'])

    status = 'ativado' if produto.is_active else 'desativado'
    messages.success(request, f'Produto "{produto.name}" {status} com sucesso.')
    return redirect('sellers:product-list')


# ---------------------------------------------------------------------------
# Controle de Estoque
# ---------------------------------------------------------------------------

@login_required
def inventory(request):
    """
    Página de controle de estoque do vendedor.

    Exibe todos os produtos com estoque por tamanho.
    Alertas visuais para estoque baixo (< 5) e zerado.
    Suporta filtro por disponibilidade e busca por nome.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    LOW_STOCK_THRESHOLD = 5
    q = request.GET.get('q', '').strip()
    disponibilidade = request.GET.get('disponibilidade', '').strip()

    produtos_qs = (
        request.user.products
        .select_related('category')
        .prefetch_related('stock_items')
        .order_by('name')
    )

    if q:
        produtos_qs = produtos_qs.filter(Q(name__icontains=q) | Q(brand__icontains=q))

    if disponibilidade == 'em_estoque':
        produtos_qs = produtos_qs.filter(stock_items__quantity__gt=0).distinct()
    elif disponibilidade == 'estoque_baixo':
        produtos_qs = produtos_qs.filter(
            stock_items__quantity__gt=0,
            stock_items__quantity__lt=LOW_STOCK_THRESHOLD
        ).distinct()
    elif disponibilidade == 'sem_estoque':
        produtos_qs = produtos_qs.exclude(stock_items__quantity__gt=0)

    # Anotações para cada produto
    produtos_data = []
    for produto in produtos_qs:
        stocks = list(produto.stock_items.order_by('size'))
        total_qty = sum(s.quantity for s in stocks)
        tem_baixo = any(0 < s.quantity < LOW_STOCK_THRESHOLD for s in stocks)
        sem_estoque = total_qty == 0
        produtos_data.append({
            'produto': produto,
            'stocks': stocks,
            'total_qty': total_qty,
            'tem_baixo': tem_baixo,
            'sem_estoque': sem_estoque,
        })

    # Estatísticas
    total_produtos = len(produtos_data)
    count_baixo = sum(1 for p in produtos_data if p['tem_baixo'])
    count_sem = sum(1 for p in produtos_data if p['sem_estoque'])

    paginator = Paginator(produtos_data, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'sellers/inventory.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'q': q,
        'disponibilidade': disponibilidade,
        'total_produtos': total_produtos,
        'count_baixo': count_baixo,
        'count_sem': count_sem,
        'LOW_STOCK_THRESHOLD': LOW_STOCK_THRESHOLD,
    })


@login_required
@require_POST
def inventory_update(request, product_pk, size):
    """
    Atualiza a quantidade de um item de estoque via POST.

    Garante que:
        - O produto pertence ao vendedor autenticado.
        - A quantidade não seja negativa.
        - O registro de estoque existe.

    POST params:
        quantity: nova quantidade (inteiro >= 0)
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    produto = get_object_or_404(Product, pk=product_pk, seller=request.user)
    stock_item = get_object_or_404(Stock, product=produto, size=size)

    try:
        nova_qty = int(request.POST.get('quantity', '').strip())
        if nova_qty < 0:
            raise ValueError('Quantidade negativa.')
    except (ValueError, AttributeError):
        messages.error(request, 'Quantidade inválida. Informe um número inteiro maior ou igual a zero.')
        return redirect('sellers:inventory')

    stock_item.quantity = nova_qty
    stock_item.save(update_fields=['quantity', 'updated_at'])

    messages.success(request, f'Estoque de "{produto.name}" (Tam. {size}) atualizado para {nova_qty} unidades.')
    return redirect('sellers:inventory')


# ---------------------------------------------------------------------------
# Vendas e Relatórios
# ---------------------------------------------------------------------------

@login_required
def sales(request):
    """
    Relatório de vendas do vendedor com filtros por período.

    Períodos disponíveis: hoje, 7d, 30d, mes, personalizado (data_inicio + data_fim).
    Considera apenas itens com pedidos em status CONFIRMED, SHIPPED ou DELIVERED.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    VALID_STATUSES = [Order.Status.CONFIRMED, Order.Status.SHIPPED, Order.Status.DELIVERED]

    periodo = request.GET.get('periodo', '30d')
    data_inicio_str = request.GET.get('data_inicio', '')
    data_fim_str = request.GET.get('data_fim', '')

    hoje = date.today()

    if periodo == 'hoje':
        data_inicio = hoje
        data_fim = hoje
    elif periodo == '7d':
        data_inicio = hoje - timedelta(days=6)
        data_fim = hoje
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
    elif periodo == 'custom' and data_inicio_str and data_fim_str:
        try:
            from datetime import datetime
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            if data_inicio > data_fim:
                data_inicio, data_fim = data_fim, data_inicio
        except ValueError:
            data_inicio = hoje - timedelta(days=29)
            data_fim = hoje
            periodo = '30d'
    else:
        data_inicio = hoje - timedelta(days=29)
        data_fim = hoje
        periodo = '30d'

    # Items do período
    items_periodo = (
        OrderItem.objects
        .filter(
            product__seller=request.user,
            order__status__in=VALID_STATUSES,
            order__created_at__date__gte=data_inicio,
            order__created_at__date__lte=data_fim,
        )
        .select_related('order', 'product')
    )

    # KPIs do período
    faturamento = sum(item.unit_price * item.quantity for item in items_periodo)
    qtd_pedidos_periodo = (
        Order.objects
        .filter(
            pk__in=items_periodo.values_list('order_id', flat=True).distinct()
        )
        .count()
    )
    ticket_medio = faturamento / qtd_pedidos_periodo if qtd_pedidos_periodo > 0 else Decimal('0.00')
    qtd_itens_vendidos = sum(item.quantity for item in items_periodo)

    # Top 5 produtos mais vendidos no período
    top_produtos_periodo = (
        items_periodo
        .values('product__id', 'product__name', 'product__brand')
        .annotate(total_qty=Sum('quantity'), total_rev=Sum('unit_price'))
        .order_by('-total_qty')[:5]
    )

    # Evolução diária no período
    delta = (data_fim - data_inicio).days + 1
    order_ids_periodo = list(
        Order.objects
        .filter(pk__in=items_periodo.values_list('order_id', flat=True).distinct())
        .values_list('id', flat=True)
    )

    pedidos_por_dia_raw = (
        OrderItem.objects
        .filter(
            product__seller=request.user,
            order__status__in=VALID_STATUSES,
            order__created_at__date__gte=data_inicio,
            order__created_at__date__lte=data_fim,
        )
        .annotate(dia=TruncDate('order__created_at'))
        .values('dia')
        .annotate(count=Count('order_id', distinct=True), receita=Sum('unit_price'))
        .order_by('dia')
    )

    dias_map = {row['dia']: {'count': row['count'], 'receita': row['receita'] or Decimal('0')} for row in pedidos_por_dia_raw}
    grafico_evolucao = []
    for i in range(delta):
        dia = data_inicio + timedelta(days=i)
        info = dias_map.get(dia, {'count': 0, 'receita': Decimal('0')})
        grafico_evolucao.append({
            'dia': dia.strftime('%d/%m'),
            'count': info['count'],
            'receita': float(info['receita']),
        })

    max_receita = max((d['receita'] for d in grafico_evolucao), default=1) or 1

    # Histórico de pedidos do período
    pedidos_hist = []
    seen = set()
    for item in items_periodo.order_by('-order__created_at'):
        if item.order_id not in seen:
            seen.add(item.order_id)
            pedidos_hist.append(item.order)

    paginator = Paginator(pedidos_hist, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'periodo': periodo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'data_inicio_str': data_inicio_str,
        'data_fim_str': data_fim_str,
        # KPIs
        'faturamento': faturamento,
        'qtd_pedidos_periodo': qtd_pedidos_periodo,
        'ticket_medio': ticket_medio,
        'qtd_itens_vendidos': qtd_itens_vendidos,
        # Gráfico
        'grafico_evolucao': grafico_evolucao,
        'max_receita': max_receita,
        # Listas
        'top_produtos_periodo': top_produtos_periodo,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
    }
    return render(request, 'sellers/sales.html', context)


# ---------------------------------------------------------------------------
# Minha Loja
# ---------------------------------------------------------------------------

@login_required
def store(request):
    """
    Gerencia as informações públicas da loja do vendedor.

    GET: exibe dados do SellerProfile.
    POST: valida e salva as alterações (store_name, description, cnpj,
          shipping_rate_per_km, shipping_distance_km).
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    seller_profile, _ = SellerProfile.objects.get_or_create(user=request.user, defaults={'store_name': request.user.full_name})

    if request.method == 'POST':
        form = SellerProfileForm(request.POST, instance=seller_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da loja atualizadas com sucesso!')
            return redirect('sellers:store')
        else:
            messages.error(request, 'Corrija os erros abaixo antes de salvar.')
    else:
        form = SellerProfileForm(instance=seller_profile)

    # Estatísticas rápidas
    total_produtos = request.user.products.filter(is_active=True).count()
    frete_estimado = seller_profile.calculate_shipping()

    return render(request, 'sellers/store.html', {
        'form': form,
        'seller_profile': seller_profile,
        'total_produtos': total_produtos,
        'frete_estimado': frete_estimado,
    })


# ---------------------------------------------------------------------------
# Perfil e Configurações
# ---------------------------------------------------------------------------

@login_required
def settings(request):
    """
    Gerencia o perfil e configurações da conta do vendedor.

    Permite editar dados pessoais (nome, e-mail) e alterar senha.
    Não permite alterar user_type, is_staff, is_superuser ou is_active.
    """
    if not request.user.is_seller:
        messages.error(request, 'Acesso restrito a vendedores.')
        return redirect('home')

    user = request.user

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Seus dados foram atualizados com sucesso!')
            return redirect('sellers:settings')
        else:
            messages.error(request, 'Corrija os erros abaixo antes de salvar.')
    else:
        user_form = UserProfileForm(instance=user)

    return render(request, 'sellers/settings.html', {
        'user_form': user_form,
        'user': user,
    })
