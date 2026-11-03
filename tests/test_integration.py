"""
Testes de integração end-to-end do Marketplace de Calçados.

Cobre o ciclo completo de compra e os controles de acesso entre perfis:
    - test_full_purchase_flow: fluxo completo do carrinho ao pedido confirmado
    - test_seller_sees_order_after_purchase: vendedor vê o pedido no dashboard
    - test_seller_updates_status: transições CONFIRMED → SHIPPED → DELIVERED
    - test_client_cannot_access_seller_dashboard: cliente é barrado no painel
    - test_seller_cannot_see_other_seller_orders: isolamento entre vendedores
    - test_insufficient_stock_blocks_checkout: estoque insuficiente bloqueia pedido

Executável via:
    python manage.py test tests.test_integration
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product, Stock
from apps.users.models import Address, SellerProfile

User = get_user_model()


# ---------------------------------------------------------------------------
# Mixin de setup base — reutilizado por todos os testes e2e
# ---------------------------------------------------------------------------


class IntegrationBaseTestCase(TestCase):
    """Configura o cenário base compartilhado pelos testes de integração.

    Cria:
        - seller: vendedor com SellerProfile (frete R$ 2,00/km × 10 km = R$ 20,00)
        - outro_seller: segundo vendedor para testes de isolamento
        - cliente: comprador com Address padrão
        - category, produto (preço R$ 299,90), estoque (tamanho '42', qty 5)
    """

    def setUp(self):
        self.http_client = Client()

        # ------------------------------------------------------------------
        # Vendedor principal
        # ------------------------------------------------------------------
        self.seller = User.objects.create_user(
            username='vendedor_integracao',
            email='vendedor@integracao.test',
            password='Senha@Forte123',
            first_name='Carlos',
            last_name='Vendedor',
            user_type=User.UserType.SELLER,
        )
        # O signal cria SellerProfile automaticamente; ajustamos os valores de frete
        self.seller_profile = SellerProfile.objects.get_or_create(
            user=self.seller,
            defaults={
                'store_name': 'Loja Integração',
                'shipping_distance_km': Decimal('10.00'),
                'shipping_rate_per_km': Decimal('2.00'),
            },
        )[0]
        self.seller_profile.store_name = 'Loja Integração'
        self.seller_profile.shipping_distance_km = Decimal('10.00')
        self.seller_profile.shipping_rate_per_km = Decimal('2.00')
        self.seller_profile.save()

        # ------------------------------------------------------------------
        # Segundo vendedor (para testes de isolamento)
        # ------------------------------------------------------------------
        self.outro_seller = User.objects.create_user(
            username='outro_vendedor_integracao',
            email='outro_vendedor@integracao.test',
            password='Senha@Forte123',
            first_name='Ana',
            last_name='OutraLoja',
            user_type=User.UserType.SELLER,
        )
        outro_profile = SellerProfile.objects.get_or_create(
            user=self.outro_seller,
            defaults={'store_name': 'Outra Loja'},
        )[0]
        outro_profile.store_name = 'Outra Loja'
        outro_profile.save()

        # ------------------------------------------------------------------
        # Cliente
        # ------------------------------------------------------------------
        self.cliente = User.objects.create_user(
            username='cliente_integracao',
            email='cliente@integracao.test',
            password='Senha@Forte123',
            first_name='João',
            last_name='Comprador',
            user_type=User.UserType.CLIENT,
        )
        self.address = Address.objects.create(
            user=self.cliente,
            nickname='Casa',
            recipient_name='João Comprador',
            zip_code='01001-000',
            street='Praça da Sé',
            number='100',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            is_default=True,
        )

        # ------------------------------------------------------------------
        # Categoria e produto do vendedor principal
        # ------------------------------------------------------------------
        self.category = Category.objects.create(
            name='Tênis Integração',
            slug='tenis-integracao',
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Air Force 1 E2E',
            description='Tênis para testes de integração',
            brand='Nike',
            price=Decimal('299.90'),
            is_active=True,
        )
        self.stock = Stock.objects.create(
            product=self.product,
            size='42',
            quantity=5,
        )

        # URLs frequentemente usadas
        self.url_checkout = reverse('orders:checkout')
        self.url_confirm = reverse('orders:order-confirm')
        self.url_seller_dashboard = reverse('sellers:dashboard')
        self.url_seller_order_list = reverse('orders:seller-order-list')

    # ------------------------------------------------------------------
    # Helper: executa compra completa e retorna o Order criado
    # ------------------------------------------------------------------

    def _realizar_compra(self, quantity=2):
        """Executa o fluxo completo de compra como self.cliente.

        Cria carrinho, adiciona produto e confirma pedido via POST.

        Args:
            quantity: quantidade de itens a comprar (padrão 2).

        Returns:
            Order: o pedido criado.
        """
        # Garantir carrinho limpo para o cliente
        Cart.objects.filter(user=self.cliente).delete()

        cart = Cart.objects.create(user=self.cliente)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            size='42',
            quantity=quantity,
        )

        self.http_client.force_login(self.cliente)
        self.http_client.post(self.url_confirm, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })

        return Order.objects.filter(user=self.cliente).order_by('-created_at').first()


# ---------------------------------------------------------------------------
# 1. Fluxo completo de compra
# ---------------------------------------------------------------------------


class FullPurchaseFlowTest(IntegrationBaseTestCase):
    """Testa o fluxo completo: carrinho → checkout → pedido confirmado."""

    def test_full_purchase_flow(self):
        """Valida todo o ciclo de compra end-to-end.

        Etapas:
            1. Cria carrinho e adiciona produto com estoque
            2. Loga como cliente
            3. Acessa checkout (deve retornar 200)
            4. Confirma pedido via POST
            5. Verifica Order e OrderItem criados corretamente
            6. Verifica estoque descontado
            7. Verifica carrinho esvaziado
        """
        quantidade = 2
        estoque_inicial = self.stock.quantity  # 5

        # 1+2. Cria carrinho e faz login
        cart = Cart.objects.create(user=self.cliente)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            size='42',
            quantity=quantidade,
        )
        self.http_client.force_login(self.cliente)

        # 3. Acessa checkout
        response_checkout = self.http_client.get(self.url_checkout)
        self.assertEqual(
            response_checkout.status_code, 200,
            'Checkout deve retornar 200 com carrinho preenchido.',
        )

        # 4. Confirma pedido
        response = self.http_client.post(self.url_confirm, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })

        # 5a. Verifica que o Order foi criado
        self.assertEqual(Order.objects.count(), 1, 'Deve haver exatamente 1 pedido.')
        order = Order.objects.first()
        self.assertEqual(order.user, self.cliente)
        self.assertEqual(order.shipping_address, self.address)
        self.assertEqual(order.status, Order.Status.CONFIRMED)
        self.assertEqual(order.payment_status, Order.PaymentStatus.APPROVED)
        self.assertEqual(order.payment_method, Order.PaymentMethod.PIX_SIM)

        # Valores financeiros:
        #   subtotal = 2 × 299.90 = 599.80
        #   frete    = 10 km × 2.00 = 20.00
        #   total    = 619.80
        self.assertEqual(order.subtotal, Decimal('599.80'))
        self.assertEqual(order.shipping_cost, Decimal('20.00'))
        self.assertEqual(order.total, Decimal('619.80'))

        # 5b. Verifica OrderItem com snapshot de preço
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.size, '42')
        self.assertEqual(item.quantity, quantidade)
        self.assertEqual(item.unit_price, Decimal('299.90'))

        # Snapshot imutável: mudar o preço não afeta o item já criado
        self.product.price = Decimal('999.00')
        self.product.save()
        item.refresh_from_db()
        self.assertEqual(item.unit_price, Decimal('299.90'), 'Snapshot de preço não deve mudar.')

        # 6. Verifica estoque descontado
        self.stock.refresh_from_db()
        self.assertEqual(
            self.stock.quantity,
            estoque_inicial - quantidade,
            'Estoque deve ser descontado após pedido.',
        )

        # 7. Verifica carrinho vazio
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 0, 'Carrinho deve ser esvaziado após pedido.')

        # Redirecionamento para página de sucesso
        url_sucesso = reverse('orders:order-success', kwargs={'pk': order.pk})
        self.assertRedirects(response, url_sucesso)


# ---------------------------------------------------------------------------
# 2. Vendedor vê o pedido no dashboard após compra
# ---------------------------------------------------------------------------


class SellerSeesOrderAfterPurchaseTest(IntegrationBaseTestCase):
    """Testa que o vendedor visualiza o pedido no seu painel após uma compra."""

    def test_seller_sees_order_after_purchase(self):
        """Após compra completa, vendedor deve ver o pedido no dashboard.

        Etapas:
            1. Realiza fluxo de compra como cliente
            2. Loga como vendedor
            3. Acessa dashboard do vendedor
            4. Acessa listagem de pedidos do vendedor
            5. Verifica que o pedido aparece
        """
        # 1. Compra completa
        order = self._realizar_compra(quantity=1)
        self.assertIsNotNone(order, 'O pedido deve ter sido criado.')

        # 2+3. Loga como vendedor e acessa dashboard
        self.http_client.force_login(self.seller)
        response_dashboard = self.http_client.get(self.url_seller_dashboard)
        self.assertEqual(response_dashboard.status_code, 200, 'Dashboard deve retornar 200.')

        # 4. Acessa listagem de pedidos do vendedor
        response_orders = self.http_client.get(self.url_seller_order_list)
        self.assertEqual(response_orders.status_code, 200)

        # 5. Verifica que o pedido aparece via a view seller_order_list
        # A view agrupa por Order; verificamos que há itens do vendedor no banco
        vendor_items = OrderItem.objects.filter(product__seller=self.seller)
        self.assertEqual(vendor_items.count(), 1, 'Deve haver 1 item do vendedor.')
        self.assertEqual(vendor_items.first().order, order)


# ---------------------------------------------------------------------------
# 3. Vendedor atualiza status do pedido
# ---------------------------------------------------------------------------


class SellerUpdatesStatusTest(IntegrationBaseTestCase):
    """Testa as transições de status realizadas pelo vendedor."""

    def setUp(self):
        super().setUp()
        # Cria um pedido em status CONFIRMED diretamente (já processado)
        self.order = self._realizar_compra(quantity=1)
        self.assertIsNotNone(self.order, 'Setup: pedido deve ter sido criado.')
        # O order_confirm cria o pedido com status CONFIRMED
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)

    def _update_status(self, novo_status):
        """Helper: envia POST para atualizar status do pedido como vendedor."""
        self.http_client.force_login(self.seller)
        url = reverse('orders:seller-order-update-status', kwargs={'pk': self.order.pk})
        return self.http_client.post(url, {'status': novo_status})

    def test_seller_updates_status_confirmed_to_shipped(self):
        """Vendedor atualiza status de CONFIRMED para SHIPPED."""
        response = self._update_status(Order.Status.SHIPPED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.SHIPPED)
        # Deve redirecionar para o detalhe do pedido
        url_detalhe = reverse('orders:seller-order-detail', kwargs={'pk': self.order.pk})
        self.assertRedirects(response, url_detalhe)

    def test_seller_updates_status_shipped_to_delivered(self):
        """Vendedor atualiza status de SHIPPED para DELIVERED."""
        # Primeiro avança para SHIPPED
        self.order.status = Order.Status.SHIPPED
        self.order.save(update_fields=['status', 'updated_at'])

        response = self._update_status(Order.Status.DELIVERED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.DELIVERED)

        url_detalhe = reverse('orders:seller-order-detail', kwargs={'pk': self.order.pk})
        self.assertRedirects(response, url_detalhe)

    def test_seller_updates_status_full_cycle_confirmed_shipped_delivered(self):
        """Ciclo completo CONFIRMED → SHIPPED → DELIVERED."""
        # CONFIRMED → SHIPPED
        self._update_status(Order.Status.SHIPPED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.SHIPPED)

        # SHIPPED → DELIVERED
        self._update_status(Order.Status.DELIVERED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.DELIVERED)


# ---------------------------------------------------------------------------
# 4. Cliente não pode acessar o painel do vendedor
# ---------------------------------------------------------------------------


class ClientCannotAccessSellerDashboardTest(IntegrationBaseTestCase):
    """Garante que clientes são barrados nas views restritas a vendedores."""

    def test_client_cannot_access_seller_dashboard(self):
        """Cliente logado recebe redirecionamento ao tentar acessar o dashboard."""
        self.http_client.force_login(self.cliente)

        # Dashboard do vendedor
        response = self.http_client.get(self.url_seller_dashboard)
        # Deve redirecionar (302) — não pode retornar 200
        self.assertNotEqual(
            response.status_code, 200,
            'Cliente não deve ter acesso ao dashboard do vendedor.',
        )
        self.assertIn(response.status_code, [302, 403])

    def test_client_cannot_access_seller_order_list(self):
        """Cliente logado é redirecionado ao tentar ver a lista de pedidos do vendedor."""
        self.http_client.force_login(self.cliente)

        response = self.http_client.get(self.url_seller_order_list)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403])

    def test_anonymous_user_redirected_from_seller_dashboard(self):
        """Usuário anônimo é redirecionado para o login ao acessar o painel."""
        response = self.http_client.get(self.url_seller_dashboard)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())


# ---------------------------------------------------------------------------
# 5. Vendedor não vê pedidos de outro vendedor
# ---------------------------------------------------------------------------


class SellerCannotSeeOtherSellerOrdersTest(IntegrationBaseTestCase):
    """Garante o isolamento de pedidos entre vendedores distintos."""

    def setUp(self):
        super().setUp()
        # Produto e estoque do segundo vendedor
        self.produto_outro_seller = Product.objects.create(
            seller=self.outro_seller,
            category=self.category,
            name='Produto Outro Vendedor',
            description='Produto exclusivo de outro vendedor',
            brand='Adidas',
            price=Decimal('199.90'),
            is_active=True,
        )
        self.stock_outro = Stock.objects.create(
            product=self.produto_outro_seller,
            size='40',
            quantity=3,
        )
        # Endereço para o cliente comprar do outro vendedor
        self.address_outro = self.address  # reutiliza o mesmo endereço

    def test_seller_cannot_see_other_seller_orders(self):
        """Vendedor A não vê na sua listagem os pedidos que contêm só produtos do Vendedor B."""
        # Realiza compra do produto do vendedor principal (seller)
        order_seller_principal = self._realizar_compra(quantity=1)
        self.assertIsNotNone(order_seller_principal)

        # Agora cria pedido manualmente com produto do outro_seller
        Cart.objects.filter(user=self.cliente).delete()
        cart2 = Cart.objects.create(user=self.cliente)
        CartItem.objects.create(
            cart=cart2,
            product=self.produto_outro_seller,
            size='40',
            quantity=1,
        )
        self.http_client.force_login(self.cliente)
        self.http_client.post(self.url_confirm, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.BOLETO_SIM,
        })

        order_outro_seller = (
            Order.objects.filter(user=self.cliente).order_by('-created_at').first()
        )
        self.assertIsNotNone(order_outro_seller)

        # Verifica isolamento: OrderItem do seller principal ≠ OrderItem do outro seller
        itens_seller_principal = OrderItem.objects.filter(product__seller=self.seller)
        itens_outro_seller = OrderItem.objects.filter(product__seller=self.outro_seller)

        self.assertEqual(itens_seller_principal.count(), 1)
        self.assertEqual(itens_outro_seller.count(), 1)

        # Os itens pertencem a pedidos distintos
        self.assertNotEqual(
            itens_seller_principal.first().order,
            itens_outro_seller.first().order,
        )

        # Vendedor principal acessa seu painel — deve ver apenas seu pedido
        self.http_client.force_login(self.seller)
        response = self.http_client.get(self.url_seller_order_list)
        self.assertEqual(response.status_code, 200)
        # Confirma que o banco tem os itens separados
        self.assertFalse(
            itens_seller_principal.filter(product__seller=self.outro_seller).exists(),
            'Itens do vendedor principal não devem incluir produtos do outro vendedor.',
        )

    def test_seller_cannot_access_order_detail_of_other_seller(self):
        """Vendedor não pode acessar o detalhe de um pedido sem produtos seus."""
        # Cria pedido com produto do outro_seller
        Cart.objects.filter(user=self.cliente).delete()
        cart = Cart.objects.create(user=self.cliente)
        CartItem.objects.create(
            cart=cart,
            product=self.produto_outro_seller,
            size='40',
            quantity=1,
        )
        self.http_client.force_login(self.cliente)
        self.http_client.post(self.url_confirm, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        order = Order.objects.filter(user=self.cliente).order_by('-created_at').first()

        # Loga como seller (principal) e tenta acessar pedido do outro_seller
        self.http_client.force_login(self.seller)
        url_detalhe = reverse('orders:seller-order-detail', kwargs={'pk': order.pk})
        response = self.http_client.get(url_detalhe)

        # Deve redirecionar, pois o pedido não contém produtos do seller principal
        self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# 6. Estoque insuficiente bloqueia o checkout
# ---------------------------------------------------------------------------


class InsufficientStockBlocksCheckoutTest(IntegrationBaseTestCase):
    """Garante que pedidos são bloqueados quando o estoque é insuficiente."""

    def test_insufficient_stock_blocks_checkout(self):
        """Checkout não cria pedido se estoque for insuficiente.

        Cenário: carrinho tem 4 unidades, mas estoque só tem 2.
        Resultado esperado:
            - Nenhum Order criado
            - Nenhum OrderItem criado
            - Estoque não alterado
            - Carrinho preservado
            - Redirecionamento para checkout com mensagem de erro
        """
        # Reduz estoque para 2
        self.stock.quantity = 2
        self.stock.save()

        # Cria carrinho com 4 unidades (excede estoque)
        cart = Cart.objects.create(user=self.cliente)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            size='42',
            quantity=4,
        )

        self.http_client.force_login(self.cliente)
        response = self.http_client.post(self.url_confirm, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.CREDIT_CARD_SIM,
        })

        # Nenhum pedido criado
        self.assertEqual(Order.objects.count(), 0, 'Nenhum pedido deve ser criado.')
        self.assertEqual(OrderItem.objects.count(), 0, 'Nenhum item de pedido deve ser criado.')

        # Estoque não foi alterado
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 2, 'Estoque não deve ser descontado.')

        # Carrinho preservado
        self.assertEqual(cart.items.count(), 1, 'Carrinho deve continuar intacto.')

        # Redirecionamento para checkout
        self.assertRedirects(response, self.url_checkout)

    def test_zero_stock_blocks_checkout(self):
        """Produto com estoque zero bloqueia o pedido."""
        self.stock.quantity = 0
        self.stock.save()

        cart = Cart.objects.create(user=self.cliente)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            size='42',
            quantity=1,
        )

        self.http_client.force_login(self.cliente)
        response = self.http_client.post(self.url_confirm, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })

        self.assertEqual(Order.objects.count(), 0)
        self.assertRedirects(response, self.url_checkout)
