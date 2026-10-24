"""
Testes de integração para o fluxo completo de compra (app orders).

Cobre:
    - Checkout com carrinho vazio (redirecionamento)
    - Checkout exibe endereços do usuário
    - Checkout calcula frete por vendedor
    - Confirmação cria pedido com dados corretos
    - Confirmação cria OrderItems com snapshot de preço
    - Confirmação desconta estoque
    - Confirmação limpa o carrinho
    - Confirmação rejeita pedido sem estoque suficiente
    - Listagem exibe apenas pedidos do próprio usuário
    - Detalhe de pedido de outro usuário retorna 404
    - Pagamento sempre APPROVED (simulado)

Executável via:
    python manage.py test tests.orders
    python manage.py test tests.orders.test_views
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
# Helpers / Mixin
# ---------------------------------------------------------------------------


class OrderTestSetUpMixin(TestCase):
    """Configura o cenário base reutilizável para todos os testes de pedidos.

    Cria:
        - cliente_user: usuário do tipo CLIENT
        - outro_user: segundo cliente para testes de isolamento
        - seller_user + SellerProfile (frete R$ 2,00/km x 10 km = R$ 20,00)
        - category, produto com preço R$ 150,00
        - estoque: tamanho '42', quantidade 5
        - cart + CartItem (1 unidade do produto, tamanho '42')
        - address: endereço padrão do cliente
    """

    def setUp(self):
        self.http_client = Client()

        # Usuarios
        self.cliente_user = User.objects.create_user(
            username='cliente_orders_test',
            email='cliente@orders.test',
            password='Senha@Forte123',
            first_name='Joao',
            last_name='Cliente',
            user_type=User.UserType.CLIENT,
        )

        self.outro_user = User.objects.create_user(
            username='outro_orders_test',
            email='outro@orders.test',
            password='Senha@Forte123',
            first_name='Maria',
            last_name='Outro',
            user_type=User.UserType.CLIENT,
        )

        self.seller_user = User.objects.create_user(
            username='seller_orders_test',
            email='seller@orders.test',
            password='Senha@Forte123',
            first_name='Loja',
            last_name='Seller',
            user_type=User.UserType.SELLER,
        )

        # SellerProfile: frete = 10 km x R$2,00 = R$20,00
        self.seller_profile = SellerProfile.objects.get_or_create(
            user=self.seller_user,
            defaults={
                'store_name': 'Loja de Teste',
                'shipping_distance_km': Decimal('10.00'),
                'shipping_rate_per_km': Decimal('2.00'),
            },
        )[0]
        # Garante valores mesmo se SellerProfile ja existia via signal
        self.seller_profile.shipping_distance_km = Decimal('10.00')
        self.seller_profile.shipping_rate_per_km = Decimal('2.00')
        self.seller_profile.save()

        # Produto + Estoque
        self.category = Category.objects.create(
            name='Tenis Teste',
            slug='tenis-teste',
        )

        self.product = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name='Tenis Runner',
            description='Tenis para corrida.',
            brand='RunBrand',
            price=Decimal('150.00'),
            is_active=True,
        )

        self.stock = Stock.objects.create(
            product=self.product,
            size='42',
            quantity=5,
        )

        # Carrinho do cliente
        self.cart = Cart.objects.create(user=self.cliente_user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            size='42',
            quantity=2,
        )

        # Endereco do cliente
        self.address = Address.objects.create(
            user=self.cliente_user,
            recipient_name='Joao Cliente',
            zip_code='01310-100',
            street='Av. Paulista',
            number='1000',
            neighborhood='Bela Vista',
            city='Sao Paulo',
            state='SP',
            is_default=True,
        )

        # URLs
        self.url_checkout = reverse('orders:checkout')
        self.url_confirm = reverse('orders:order-confirm')
        self.url_order_list = reverse('orders:order-list')

    def _post_confirm(self, payment_method=None, address_id=None):
        """Atalho para enviar POST para order_confirm com dados validos."""
        payload = {
            'address_id': str(address_id or self.address.pk),
            'payment_method': payment_method or Order.PaymentMethod.PIX_SIM,
        }
        return self.http_client.post(self.url_confirm, payload)

    def _criar_pedido_para(self, user, address=None):
        """Cria um Order completo para um usuario (sem carrinho)."""
        addr = address or self.address
        order = Order.objects.create(
            user=user,
            shipping_address=addr,
            subtotal=Decimal('150.00'),
            shipping_cost=Decimal('20.00'),
            total=Decimal('170.00'),
            payment_method=Order.PaymentMethod.PIX_SIM,
            payment_status=Order.PaymentStatus.APPROVED,
            status=Order.Status.CONFIRMED,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            size='42',
            quantity=1,
            unit_price=Decimal('150.00'),
        )
        return order


# ---------------------------------------------------------------------------
# 1. Checkout - carrinho vazio
# ---------------------------------------------------------------------------


class TestCheckoutComCarrinhoVazio(OrderTestSetUpMixin):
    """Checkout com carrinho vazio deve redirecionar para o carrinho."""

    def test_checkout_with_empty_cart_redirects(self):
        """Carrinho vazio: checkout redireciona para cart:cart-detail."""
        self.http_client.force_login(self.cliente_user)

        # Esvazia o carrinho do cliente
        self.cart_item.delete()

        response = self.http_client.get(self.url_checkout)

        self.assertRedirects(
            response,
            reverse('cart:cart-detail'),
            fetch_redirect_response=False,
            msg_prefix='Carrinho vazio deve redirecionar para a pagina do carrinho.',
        )

    def test_checkout_sem_carrinho_redireciona(self):
        """Usuario sem Cart criado e redirecionado para o carrinho."""
        self.http_client.force_login(self.outro_user)  # outro_user nao tem carrinho

        response = self.http_client.get(self.url_checkout)

        self.assertRedirects(
            response,
            reverse('cart:cart-detail'),
            fetch_redirect_response=False,
        )


# ---------------------------------------------------------------------------
# 2. Checkout - exibe enderecos
# ---------------------------------------------------------------------------


class TestCheckoutExibeEnderecos(OrderTestSetUpMixin):
    """Checkout deve listar os enderecos do usuario autenticado."""

    def test_checkout_shows_addresses(self):
        """Checkout lista enderecos do usuario no contexto."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.get(self.url_checkout)

        self.assertEqual(response.status_code, 200)
        self.assertIn('addresses', response.context)

        address_ids = [a.pk for a in response.context['addresses']]
        self.assertIn(
            self.address.pk,
            address_ids,
            'O endereco cadastrado deve aparecer no checkout.',
        )

    def test_checkout_preseleciona_endereco_padrao(self):
        """O endereco padrao deve vir pre-selecionado no contexto."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.get(self.url_checkout)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['preselected_id'],
            self.address.pk,
            'O endereco padrao deve ser pre-selecionado.',
        )

    def test_checkout_nao_exibe_enderecos_de_outro_usuario(self):
        """Checkout nao deve exibir enderecos de outros usuarios."""
        Address.objects.create(
            user=self.outro_user,
            recipient_name='Maria Outro',
            zip_code='20040-020',
            street='Rua da Quitanda',
            number='5',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
        )

        self.http_client.force_login(self.cliente_user)
        response = self.http_client.get(self.url_checkout)

        for addr in response.context['addresses']:
            self.assertEqual(
                addr.user_id,
                self.cliente_user.pk,
                'Checkout so deve exibir enderecos do usuario logado.',
            )
        self.assertEqual(len(list(response.context['addresses'])), 1)


# ---------------------------------------------------------------------------
# 3. Checkout - calculo de frete
# ---------------------------------------------------------------------------


class TestCheckoutCalculaFrete(OrderTestSetUpMixin):
    """Checkout deve calcular o frete corretamente por vendedor."""

    def test_checkout_calculates_shipping(self):
        """Frete = distancia x taxa (10 km x R$2,00 = R$20,00)."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.get(self.url_checkout)

        self.assertEqual(response.status_code, 200)

        total_shipping = response.context['total_shipping']
        self.assertEqual(
            total_shipping,
            Decimal('20.00'),
            f'Frete esperado R$20,00, recebido R${total_shipping}.',
        )

    def test_checkout_subtotal_correto(self):
        """Subtotal = preco x quantidade (R$150,00 x 2 = R$300,00)."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.get(self.url_checkout)

        subtotal = response.context['subtotal']
        self.assertEqual(
            subtotal,
            Decimal('300.00'),
            f'Subtotal esperado R$300,00, recebido R${subtotal}.',
        )

    def test_checkout_total_correto(self):
        """Total = subtotal + frete (R$300,00 + R$20,00 = R$320,00)."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.get(self.url_checkout)

        total = response.context['total']
        self.assertEqual(
            total,
            Decimal('320.00'),
            f'Total esperado R$320,00, recebido R${total}.',
        )


# ---------------------------------------------------------------------------
# 4. Confirmacao - pedido criado com dados corretos
# ---------------------------------------------------------------------------


class TestOrderConfirmCriaOrder(OrderTestSetUpMixin):
    """order_confirm deve criar o Order com todos os dados corretos."""

    def test_order_confirm_creates_order(self):
        """POST valido cria Order com status CONFIRMED e dados financeiros."""
        self.http_client.force_login(self.cliente_user)

        self.assertEqual(Order.objects.count(), 0)

        response = self._post_confirm()

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()

        self.assertRedirects(
            response,
            reverse('orders:order-success', kwargs={'pk': order.pk}),
            fetch_redirect_response=False,
        )

    def test_order_confirm_dados_financeiros(self):
        """Order criado deve ter subtotal, frete e total corretos."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm()

        order = Order.objects.first()
        self.assertEqual(order.subtotal, Decimal('300.00'))      # 2 x R$150
        self.assertEqual(order.shipping_cost, Decimal('20.00'))  # frete simulado
        self.assertEqual(order.total, Decimal('320.00'))          # 300 + 20

    def test_order_confirm_associa_endereco(self):
        """Order deve ficar associado ao endereco escolhido no POST."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm()

        order = Order.objects.first()
        self.assertEqual(order.shipping_address_id, self.address.pk)

    def test_order_confirm_associa_usuario(self):
        """Order deve estar associado ao usuario autenticado."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm()

        order = Order.objects.first()
        self.assertEqual(order.user_id, self.cliente_user.pk)

    def test_order_confirm_requer_autenticacao(self):
        """POST sem autenticacao redireciona para login."""
        response = self._post_confirm()

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_confirm}',
            fetch_redirect_response=False,
        )
        self.assertEqual(Order.objects.count(), 0)


# ---------------------------------------------------------------------------
# 5. Confirmacao - OrderItems com snapshot de preco
# ---------------------------------------------------------------------------


class TestOrderConfirmSnapshot(OrderTestSetUpMixin):
    """Os OrderItems devem registrar o preco no momento da compra (snapshot)."""

    def test_order_confirm_creates_items_with_snapshot(self):
        """unit_price do OrderItem deve ser o preco do produto no momento da compra."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm()

        order = Order.objects.first()
        items = list(order.items.all())

        self.assertEqual(len(items), 1)
        item = items[0]

        self.assertEqual(
            item.unit_price,
            Decimal('150.00'),
            'unit_price deve ser o snapshot do preco no momento da compra.',
        )
        self.assertEqual(item.size, '42')
        self.assertEqual(item.quantity, 2)

    def test_snapshot_nao_muda_com_alteracao_de_preco(self):
        """Alterar o preco do produto apos a compra nao deve afetar o OrderItem."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm()

        # Altera o preco do produto
        self.product.price = Decimal('999.00')
        self.product.save()

        order = Order.objects.first()
        item = order.items.first()

        self.assertEqual(
            item.unit_price,
            Decimal('150.00'),
            'Snapshot de preco nao deve mudar apos alteracao do produto.',
        )


# ---------------------------------------------------------------------------
# 6. Confirmacao - desconta estoque
# ---------------------------------------------------------------------------


class TestOrderConfirmDescontaEstoque(OrderTestSetUpMixin):
    """order_confirm deve decrementar o estoque dos produtos comprados."""

    def test_order_confirm_decrements_stock(self):
        """Estoque deve ser decrementado pela quantidade do CartItem."""
        self.http_client.force_login(self.cliente_user)

        estoque_antes = self.stock.quantity  # 5

        self._post_confirm()  # compra 2 unidades

        self.stock.refresh_from_db()
        self.assertEqual(
            self.stock.quantity,
            estoque_antes - 2,
            f'Estoque deve ser reduzido de {estoque_antes} para {estoque_antes - 2}.',
        )


# ---------------------------------------------------------------------------
# 7. Confirmacao - limpa o carrinho
# ---------------------------------------------------------------------------


class TestOrderConfirmLimpaCarrinho(OrderTestSetUpMixin):
    """Apos a confirmacao, o carrinho deve ficar vazio."""

    def test_order_confirm_clears_cart(self):
        """CartItems devem ser deletados apos a confirmacao do pedido."""
        self.http_client.force_login(self.cliente_user)

        self.assertEqual(self.cart.items.count(), 1)

        self._post_confirm()

        self.assertEqual(
            self.cart.items.count(),
            0,
            'O carrinho deve estar vazio apos a confirmacao do pedido.',
        )


# ---------------------------------------------------------------------------
# 8. Confirmacao - estoque insuficiente
# ---------------------------------------------------------------------------


class TestOrderConfirmEstoqueInsuficiente(OrderTestSetUpMixin):
    """order_confirm deve rejeitar pedido quando o estoque e insuficiente."""

    def test_order_confirm_insufficient_stock(self):
        """Pedido com quantidade maior que o estoque e rejeitado."""
        self.http_client.force_login(self.cliente_user)

        # Reduz estoque para 1, mas carrinho tem quantidade 2
        self.stock.quantity = 1
        self.stock.save()

        response = self._post_confirm()

        # Deve redirecionar de volta para o checkout com mensagem de erro
        self.assertRedirects(
            response,
            self.url_checkout,
            fetch_redirect_response=False,
        )

        # Nenhum pedido deve ter sido criado
        self.assertEqual(Order.objects.count(), 0)

    def test_order_confirm_insufficient_stock_nao_decrementa(self):
        """Estoque nao deve ser decrementado quando o pedido e rejeitado."""
        self.http_client.force_login(self.cliente_user)

        self.stock.quantity = 1
        self.stock.save()

        self._post_confirm()

        self.stock.refresh_from_db()
        self.assertEqual(
            self.stock.quantity,
            1,
            'Estoque nao deve ser alterado quando o pedido e rejeitado.',
        )

    def test_order_confirm_sem_estoque_zero(self):
        """Produto com estoque zerado deve rejeitar o pedido."""
        self.http_client.force_login(self.cliente_user)

        self.stock.quantity = 0
        self.stock.save()

        response = self._post_confirm()

        self.assertRedirects(
            response,
            self.url_checkout,
            fetch_redirect_response=False,
        )
        self.assertEqual(Order.objects.count(), 0)


# ---------------------------------------------------------------------------
# 9. Listagem - apenas pedidos do proprio usuario
# ---------------------------------------------------------------------------


class TestOrderListProprioPedido(OrderTestSetUpMixin):
    """order_list deve exibir apenas os pedidos do usuario autenticado."""

    def test_order_list_shows_own_orders(self):
        """Listagem exibe os pedidos do proprio usuario."""
        self.http_client.force_login(self.cliente_user)

        pedido = self._criar_pedido_para(self.cliente_user)

        response = self.http_client.get(self.url_order_list)

        self.assertEqual(response.status_code, 200)
        orders_na_pagina = list(response.context['page_obj'])
        order_ids = [o.pk for o in orders_na_pagina]

        self.assertIn(
            pedido.pk,
            order_ids,
            'Pedido do usuario deve aparecer na listagem.',
        )

    def test_order_list_nao_exibe_pedidos_de_outros(self):
        """Listagem nao deve exibir pedidos de outros usuarios."""
        outro_address = Address.objects.create(
            user=self.outro_user,
            recipient_name='Maria Outro',
            zip_code='20040-020',
            street='Rua da Quitanda',
            number='5',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
        )

        pedido_outro = self._criar_pedido_para(self.outro_user, address=outro_address)

        self.http_client.force_login(self.cliente_user)
        response = self.http_client.get(self.url_order_list)

        order_ids = [o.pk for o in response.context['page_obj']]
        self.assertNotIn(
            pedido_outro.pk,
            order_ids,
            'Pedido de outro usuario nao deve aparecer na listagem.',
        )

    def test_order_list_requer_autenticacao(self):
        """Acesso sem autenticacao redireciona para login."""
        response = self.http_client.get(self.url_order_list)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_order_list}',
            fetch_redirect_response=False,
        )


# ---------------------------------------------------------------------------
# 10. Detalhe - pedido de outro usuario retorna 404
# ---------------------------------------------------------------------------


class TestOrderDetailOutroUsuario404(OrderTestSetUpMixin):
    """order_detail deve retornar 404 ao tentar acessar pedido de outro usuario."""

    def test_order_detail_other_user_404(self):
        """Acesso ao detalhe de pedido de outro usuario retorna 404."""
        outro_address = Address.objects.create(
            user=self.outro_user,
            recipient_name='Maria Outro',
            zip_code='20040-020',
            street='Rua da Quitanda',
            number='5',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
        )
        pedido_outro = self._criar_pedido_para(self.outro_user, address=outro_address)

        self.http_client.force_login(self.cliente_user)

        url_detalhe = reverse('orders:order-detail', kwargs={'pk': pedido_outro.pk})
        response = self.http_client.get(url_detalhe)

        self.assertEqual(
            response.status_code,
            404,
            'Acesso ao pedido de outro usuario deve retornar 404.',
        )

    def test_order_detail_proprio_pedido_ok(self):
        """Acesso ao detalhe do proprio pedido retorna 200."""
        pedido = self._criar_pedido_para(self.cliente_user)

        self.http_client.force_login(self.cliente_user)

        url_detalhe = reverse('orders:order-detail', kwargs={'pk': pedido.pk})
        response = self.http_client.get(url_detalhe)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')

    def test_order_detail_requer_autenticacao(self):
        """Acesso sem autenticacao redireciona para login."""
        pedido = self._criar_pedido_para(self.cliente_user)

        url_detalhe = reverse('orders:order-detail', kwargs={'pk': pedido.pk})
        response = self.http_client.get(url_detalhe)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={url_detalhe}',
            fetch_redirect_response=False,
        )


# ---------------------------------------------------------------------------
# 11. Pagamento simulado - sempre APPROVED
# ---------------------------------------------------------------------------


class TestPaymentStatusApproved(OrderTestSetUpMixin):
    """O pagamento simulado deve sempre resultar em status APPROVED."""

    def test_payment_status_approved(self):
        """Pedido confirmado tem payment_status = APPROVED (simulacao)."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm(payment_method=Order.PaymentMethod.PIX_SIM)

        order = Order.objects.first()
        self.assertEqual(
            order.payment_status,
            Order.PaymentStatus.APPROVED,
            'Pagamento simulado deve sempre ser APPROVED.',
        )

    def test_payment_status_approved_para_cartao_credito(self):
        """Pagamento por cartao de credito (simulado) tambem deve ser APPROVED."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm(payment_method=Order.PaymentMethod.CREDIT_CARD_SIM)

        order = Order.objects.first()
        self.assertEqual(order.payment_status, Order.PaymentStatus.APPROVED)

    def test_payment_status_approved_para_boleto(self):
        """Pagamento por boleto (simulado) tambem deve ser APPROVED."""
        self.http_client.force_login(self.cliente_user)

        self._post_confirm(payment_method=Order.PaymentMethod.BOLETO_SIM)

        order = Order.objects.first()
        self.assertEqual(order.payment_status, Order.PaymentStatus.APPROVED)

    def test_payment_method_invalido_rejeitado(self):
        """Metodo de pagamento invalido deve redirecionar com erro."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.post(self.url_confirm, {
            'address_id': str(self.address.pk),
            'payment_method': 'METODO_INVALIDO',
        })

        self.assertRedirects(
            response,
            self.url_checkout,
            fetch_redirect_response=False,
        )
        self.assertEqual(Order.objects.count(), 0)

    def test_order_confirm_sem_endereco_rejeitado(self):
        """POST sem address_id deve redirecionar com erro."""
        self.http_client.force_login(self.cliente_user)

        response = self.http_client.post(self.url_confirm, {
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })

        self.assertRedirects(
            response,
            self.url_checkout,
            fetch_redirect_response=False,
        )
        self.assertEqual(Order.objects.count(), 0)
