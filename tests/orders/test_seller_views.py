
"""
Testes das views de pedidos do vendedor (seller_order_list, seller_order_update_status).

Cobre:
    - test_seller_order_list_shows_own: listagem exibe apenas pedidos com produtos do vendedor
    - test_seller_order_update_status: atualização de status válida
    - test_seller_order_update_invalid_transition: transição inválida rejeitada
    - test_client_forbidden_on_seller_views: cliente não acessa views de vendedor

Executável via:
    python manage.py test tests.orders.test_seller_views
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product, Stock
from apps.users.models import Address, SellerProfile

User = get_user_model()


# ---------------------------------------------------------------------------
# Mixin de setup compartilhado
# ---------------------------------------------------------------------------


class SellerViewsBaseTestCase(TestCase):
    """Setup base para os testes das views de pedidos do vendedor.

    Cria:
        - seller_a: vendedor principal com produto e estoque
        - seller_b: segundo vendedor com produto e estoque (para isolamento)
        - cliente: comprador com endereço padrão
        - order_a: pedido do cliente com produto do seller_a (status CONFIRMED)
        - order_b: pedido do cliente com produto do seller_b (status CONFIRMED)
    """

    def setUp(self):
        self.http_client = Client()

        # ------------------------------------------------------------------
        # Vendedor A — dono dos itens de order_a
        # ------------------------------------------------------------------
        self.seller_a = User.objects.create_user(
            username='seller_a_views_test',
            email='seller_a@views.test',
            password='Senha@Forte123',
            first_name='Vendedor',
            last_name='Alpha',
            user_type=User.UserType.SELLER,
        )
        self.profile_a = SellerProfile.objects.get_or_create(
            user=self.seller_a,
            defaults={
                'store_name': 'Loja Alpha',
                'shipping_distance_km': Decimal('5.00'),
                'shipping_rate_per_km': Decimal('2.00'),
            },
        )[0]
        self.profile_a.store_name = 'Loja Alpha'
        self.profile_a.shipping_distance_km = Decimal('5.00')
        self.profile_a.shipping_rate_per_km = Decimal('2.00')
        self.profile_a.save()

        # ------------------------------------------------------------------
        # Vendedor B — dono dos itens de order_b
        # ------------------------------------------------------------------
        self.seller_b = User.objects.create_user(
            username='seller_b_views_test',
            email='seller_b@views.test',
            password='Senha@Forte123',
            first_name='Vendedor',
            last_name='Beta',
            user_type=User.UserType.SELLER,
        )
        profile_b = SellerProfile.objects.get_or_create(
            user=self.seller_b,
            defaults={'store_name': 'Loja Beta'},
        )[0]
        profile_b.store_name = 'Loja Beta'
        profile_b.save()

        # ------------------------------------------------------------------
        # Cliente
        # ------------------------------------------------------------------
        self.cliente = User.objects.create_user(
            username='cliente_seller_views_test',
            email='cliente@views.test',
            password='Senha@Forte123',
            first_name='Maria',
            last_name='Compradora',
            user_type=User.UserType.CLIENT,
        )
        self.address = Address.objects.create(
            user=self.cliente,
            nickname='Trabalho',
            recipient_name='Maria Compradora',
            zip_code='04578-000',
            street='Av. Engenheiro Luís Carlos Berrini',
            number='500',
            neighborhood='Itaim Bibi',
            city='São Paulo',
            state='SP',
            is_default=True,
        )

        # ------------------------------------------------------------------
        # Categoria e produtos
        # ------------------------------------------------------------------
        self.category = Category.objects.create(
            name='Tênis SellerViews',
            slug='tenis-seller-views',
        )
        self.produto_a = Product.objects.create(
            seller=self.seller_a,
            category=self.category,
            name='Produto Seller A',
            description='Produto do vendedor A',
            brand='Nike',
            price=Decimal('350.00'),
            is_active=True,
        )
        self.stock_a = Stock.objects.create(
            product=self.produto_a,
            size='41',
            quantity=10,
        )

        self.produto_b = Product.objects.create(
            seller=self.seller_b,
            category=self.category,
            name='Produto Seller B',
            description='Produto do vendedor B',
            brand='Adidas',
            price=Decimal('280.00'),
            is_active=True,
        )
        self.stock_b = Stock.objects.create(
            product=self.produto_b,
            size='39',
            quantity=8,
        )

        # ------------------------------------------------------------------
        # Pedido A: contém produto do seller_a
        # ------------------------------------------------------------------
        self.order_a = Order.objects.create(
            user=self.cliente,
            shipping_address=self.address,
            subtotal=Decimal('350.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('360.00'),
            payment_method=Order.PaymentMethod.PIX_SIM,
            payment_status=Order.PaymentStatus.APPROVED,
            status=Order.Status.CONFIRMED,
        )
        self.item_a = OrderItem.objects.create(
            order=self.order_a,
            product=self.produto_a,
            size='41',
            quantity=1,
            unit_price=Decimal('350.00'),
        )

        # ------------------------------------------------------------------
        # Pedido B: contém produto do seller_b
        # ------------------------------------------------------------------
        self.order_b = Order.objects.create(
            user=self.cliente,
            shipping_address=self.address,
            subtotal=Decimal('280.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('280.00'),
            payment_method=Order.PaymentMethod.CREDIT_CARD_SIM,
            payment_status=Order.PaymentStatus.APPROVED,
            status=Order.Status.CONFIRMED,
        )
        self.item_b = OrderItem.objects.create(
            order=self.order_b,
            product=self.produto_b,
            size='39',
            quantity=1,
            unit_price=Decimal('280.00'),
        )

        # URLs
        self.url_seller_order_list = reverse('orders:seller-order-list')
        self.url_update_status_a = reverse(
            'orders:seller-order-update-status', kwargs={'pk': self.order_a.pk}
        )
        self.url_update_status_b = reverse(
            'orders:seller-order-update-status', kwargs={'pk': self.order_b.pk}
        )


# ---------------------------------------------------------------------------
# 1. Listagem exibe apenas pedidos do próprio vendedor
# ---------------------------------------------------------------------------


class SellerOrderListShowsOwnTest(SellerViewsBaseTestCase):
    """Testa que a view seller_order_list exibe apenas pedidos do vendedor logado."""

    def test_seller_order_list_shows_own(self):
        """Vendedor A vê apenas seus itens — não vê itens do Vendedor B."""
        self.http_client.force_login(self.seller_a)
        response = self.http_client.get(self.url_seller_order_list)

        self.assertEqual(response.status_code, 200)

        # Verifica no banco que apenas os itens de seller_a pertencem ao order_a
        itens_seller_a = OrderItem.objects.filter(product__seller=self.seller_a)
        itens_seller_b = OrderItem.objects.filter(product__seller=self.seller_b)

        self.assertEqual(itens_seller_a.count(), 1)
        self.assertEqual(itens_seller_b.count(), 1)

        # Os itens pertencem a pedidos diferentes
        self.assertEqual(itens_seller_a.first().order, self.order_a)
        self.assertEqual(itens_seller_b.first().order, self.order_b)

        # Itens de seller_a não contêm produtos de seller_b
        self.assertFalse(
            itens_seller_a.filter(product__seller=self.seller_b).exists(),
        )

    def test_seller_order_list_other_seller_sees_own(self):
        """Vendedor B, ao acessar, vê apenas seus próprios itens."""
        self.http_client.force_login(self.seller_b)
        response = self.http_client.get(self.url_seller_order_list)

        self.assertEqual(response.status_code, 200)

        itens_seller_b = OrderItem.objects.filter(product__seller=self.seller_b)
        self.assertEqual(itens_seller_b.count(), 1)
        self.assertEqual(itens_seller_b.first().order, self.order_b)

    def test_seller_order_list_requires_login(self):
        """Usuário anônimo é redirecionado ao tentar acessar a listagem."""
        response = self.http_client.get(self.url_seller_order_list)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())


# ---------------------------------------------------------------------------
# 2. Atualização de status válida
# ---------------------------------------------------------------------------


class SellerOrderUpdateStatusTest(SellerViewsBaseTestCase):
    """Testa a atualização de status por parte do vendedor."""

    def test_seller_order_update_status(self):
        """Vendedor atualiza status de CONFIRMED para SHIPPED com sucesso."""
        self.http_client.force_login(self.seller_a)

        response = self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.SHIPPED},
        )

        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.SHIPPED)

        url_detalhe = reverse('orders:seller-order-detail', kwargs={'pk': self.order_a.pk})
        self.assertRedirects(response, url_detalhe)

    def test_seller_order_update_status_confirmed_to_cancelled(self):
        """Vendedor pode cancelar um pedido CONFIRMED."""
        self.http_client.force_login(self.seller_a)

        self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.CANCELLED},
        )

        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.CANCELLED)

    def test_seller_order_update_status_full_sequence(self):
        """Ciclo completo: CONFIRMED → SHIPPED → DELIVERED."""
        self.http_client.force_login(self.seller_a)

        # CONFIRMED → SHIPPED
        self.http_client.post(self.url_update_status_a, {'status': Order.Status.SHIPPED})
        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.SHIPPED)

        # SHIPPED → DELIVERED
        self.http_client.post(self.url_update_status_a, {'status': Order.Status.DELIVERED})
        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.DELIVERED)


# ---------------------------------------------------------------------------
# 3. Transição inválida é rejeitada
# ---------------------------------------------------------------------------


class SellerOrderUpdateInvalidTransitionTest(SellerViewsBaseTestCase):
    """Testa que transições de status inválidas são rejeitadas pela view."""

    def test_seller_order_update_invalid_transition_skip_step(self):
        """Pular etapa (CONFIRMED → DELIVERED) é rejeitado — status não muda."""
        self.http_client.force_login(self.seller_a)

        self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.DELIVERED},
        )

        self.order_a.refresh_from_db()
        self.assertEqual(
            self.order_a.status,
            Order.Status.CONFIRMED,
            'Pular etapa não deve alterar o status do pedido.',
        )

    def test_seller_order_update_invalid_transition_retrograde(self):
        """Retroceder status (SHIPPED → CONFIRMED) é rejeitado."""
        # Avança para SHIPPED primeiro
        self.order_a.status = Order.Status.SHIPPED
        self.order_a.save(update_fields=['status', 'updated_at'])

        self.http_client.force_login(self.seller_a)
        self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.CONFIRMED},
        )

        self.order_a.refresh_from_db()
        self.assertEqual(
            self.order_a.status,
            Order.Status.SHIPPED,
            'Retroceder status não deve ser permitido.',
        )

    def test_seller_order_update_invalid_status_value(self):
        """Valor de status desconhecido é rejeitado — status não muda."""
        self.http_client.force_login(self.seller_a)

        self.http_client.post(
            self.url_update_status_a,
            {'status': 'INEXISTENTE'},
        )

        self.order_a.refresh_from_db()
        self.assertEqual(
            self.order_a.status,
            Order.Status.CONFIRMED,
            'Status inválido não deve alterar o pedido.',
        )

    def test_seller_cannot_update_status_of_delivered_order(self):
        """Pedido DELIVERED é estado final — qualquer atualização é rejeitada."""
        self.order_a.status = Order.Status.DELIVERED
        self.order_a.save(update_fields=['status', 'updated_at'])

        self.http_client.force_login(self.seller_a)
        self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.CANCELLED},
        )

        self.order_a.refresh_from_db()
        self.assertEqual(
            self.order_a.status,
            Order.Status.DELIVERED,
            'Estado final DELIVERED não deve permitir transições.',
        )


# ---------------------------------------------------------------------------
# 4. Cliente não acessa views de vendedor
# ---------------------------------------------------------------------------


class ClientForbiddenOnSellerViewsTest(SellerViewsBaseTestCase):
    """Verifica que clientes são impedidos de acessar as views restritas a vendedores."""

    def test_client_forbidden_on_seller_order_list(self):
        """Cliente recebe redirecionamento ao acessar listagem de pedidos do vendedor."""
        self.http_client.force_login(self.cliente)
        response = self.http_client.get(self.url_seller_order_list)

        self.assertNotEqual(
            response.status_code, 200,
            'Cliente não deve ter acesso à listagem de pedidos do vendedor.',
        )
        self.assertIn(response.status_code, [302, 403])

    def test_client_forbidden_on_seller_order_update_status(self):
        """Cliente não pode alterar o status de um pedido pelo endpoint do vendedor."""
        self.http_client.force_login(self.cliente)

        response = self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.SHIPPED},
        )

        # Status não deve ter mudado
        self.order_a.refresh_from_db()
        self.assertEqual(
            self.order_a.status,
            Order.Status.CONFIRMED,
            'Cliente não deve conseguir alterar status de pedido.',
        )
        # Resposta não deve ser 200 OK direto
        self.assertNotEqual(response.status_code, 200)

    def test_client_forbidden_on_seller_order_detail(self):
        """Cliente não pode acessar o detalhe de pedido via view do vendedor."""
        self.http_client.force_login(self.cliente)
        url_detalhe = reverse('orders:seller-order-detail', kwargs={'pk': self.order_a.pk})
        response = self.http_client.get(url_detalhe)

        self.assertNotEqual(
            response.status_code, 200,
            'Cliente não deve ter acesso à view de detalhe do vendedor.',
        )

    def test_anonymous_user_redirected_from_seller_update_status(self):
        """Usuário anônimo é redirecionado ao tentar atualizar status."""
        response = self.http_client.post(
            self.url_update_status_a,
            {'status': Order.Status.SHIPPED},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

        # Status não alterado
        self.order_a.refresh_from_db()
        self.assertEqual(self.order_a.status, Order.Status.CONFIRMED)
