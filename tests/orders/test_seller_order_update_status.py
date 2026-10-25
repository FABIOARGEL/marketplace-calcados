"""
Testes de integração para atualização de status de pedidos pelo vendedor.

Cobre:
    - Acesso negado a não-vendedores (cliente e anônimo)
    - Acesso negado a vendedor sem itens no pedido
    - Transições válidas: PENDING→CONFIRMED, CONFIRMED→SHIPPED, SHIPPED→DELIVERED
    - Transição para CANCELLED a partir de qualquer status não-final
    - Rejeição de status inválido (valor fora do enum)
    - Rejeição de pular etapa (ex: PENDING→SHIPPED)
    - Rejeição de retroceder (ex: CONFIRMED→PENDING)
    - Rejeição de transição a partir de estado final (DELIVERED, CANCELLED)
    - Mensagem de sucesso após atualização válida
    - Mensagem de erro nas rejeições

Executável via:
    python manage.py test tests.orders.test_seller_order_update_status
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
# Mixin de setup
# ---------------------------------------------------------------------------


class SellerOrderStatusSetUpMixin(TestCase):
    """Configura o cenário base para os testes de atualização de status.

    Cria:
        - seller_user  + SellerProfile
        - outro_seller + SellerProfile (para testar isolamento)
        - cliente_user + Address
        - category, product (de seller_user), stock
        - order (PENDING) com 1 OrderItem do seller_user
    """

    def setUp(self):
        self.http_client = Client()

        # Vendedor dono dos produtos
        self.seller_user = User.objects.create_user(
            username='seller_status_test',
            email='seller@status.test',
            password='Senha@Forte123',
            first_name='Vendedor',
            last_name='Status',
            user_type=User.UserType.SELLER,
        )
        self.seller_profile = SellerProfile.objects.get_or_create(
            user=self.seller_user,
            defaults={
                'store_name': 'Loja Status',
                'shipping_distance_km': Decimal('5.00'),
                'shipping_rate_per_km': Decimal('2.00'),
            },
        )[0]

        # Outro vendedor (sem itens no pedido)
        self.outro_seller = User.objects.create_user(
            username='outro_seller_status',
            email='outro_seller@status.test',
            password='Senha@Forte123',
            user_type=User.UserType.SELLER,
        )
        SellerProfile.objects.get_or_create(
            user=self.outro_seller,
            defaults={'store_name': 'Outra Loja'},
        )

        # Cliente
        self.cliente_user = User.objects.create_user(
            username='cliente_status_test',
            email='cliente@status.test',
            password='Senha@Forte123',
            user_type=User.UserType.CLIENT,
        )

        # Endereço do cliente
        self.address = Address.objects.create(
            user=self.cliente_user,
            recipient_name='Cliente Status',
            zip_code='01310-100',
            street='Av. Paulista',
            number='1',
            neighborhood='Bela Vista',
            city='Sao Paulo',
            state='SP',
            is_default=True,
        )

        # Produto + Estoque
        self.category = Category.objects.create(
            name='Categoria Status',
            slug='categoria-status',
        )
        self.product = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name='Tenis Status',
            description='Desc.',
            brand='Brand',
            price=Decimal('200.00'),
            is_active=True,
        )
        self.stock = Stock.objects.create(
            product=self.product,
            size='41',
            quantity=10,
        )

        # Pedido base no status PENDING
        self.order = Order.objects.create(
            user=self.cliente_user,
            shipping_address=self.address,
            subtotal=Decimal('200.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('210.00'),
            payment_method=Order.PaymentMethod.PIX_SIM,
            payment_status=Order.PaymentStatus.APPROVED,
            status=Order.Status.PENDING,
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            size='41',
            quantity=1,
            unit_price=Decimal('200.00'),
        )

        self.url_update = reverse(
            'orders:seller-order-update-status',
            kwargs={'pk': self.order.pk},
        )
        self.url_detail = reverse(
            'orders:seller-order-detail',
            kwargs={'pk': self.order.pk},
        )

    def _post_status(self, status, user=None):
        """Atalho: POST para seller_order_update_status com o status informado."""
        if user is None:
            user = self.seller_user
        self.http_client.force_login(user)
        return self.http_client.post(self.url_update, {'status': status})

    def _set_order_status(self, status):
        """Altera diretamente o status do pedido no banco (sem passar pela view)."""
        self.order.status = status
        self.order.save(update_fields=['status', 'updated_at'])
        self.order.refresh_from_db()


# ---------------------------------------------------------------------------
# 1. Controle de acesso
# ---------------------------------------------------------------------------


class TestSellerOrderUpdateStatusAcesso(SellerOrderStatusSetUpMixin):
    """Verificações de controle de acesso à view de atualização de status."""

    def test_anonimo_redirecionado_para_login(self):
        """Usuário não autenticado deve ser redirecionado para a página de login."""
        response = self.http_client.post(self.url_update, {'status': 'CONFIRMED'})
        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_update}',
            fetch_redirect_response=False,
        )

    def test_cliente_nao_pode_atualizar_status(self):
        """Usuário do tipo CLIENT não pode atualizar o status de pedidos."""
        response = self._post_status('CONFIRMED', user=self.cliente_user)
        # Deve redirecionar para home (acesso negado)
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.status,
            Order.Status.PENDING,
            'Status não deve ser alterado por um cliente.',
        )

    def test_vendedor_sem_itens_no_pedido_nao_pode_atualizar(self):
        """Vendedor que não possui itens no pedido não pode alterar o status."""
        response = self._post_status('CONFIRMED', user=self.outro_seller)
        self.assertRedirects(
            response,
            reverse('orders:seller-order-list'),
            fetch_redirect_response=False,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING)


# ---------------------------------------------------------------------------
# 2. Transições válidas
# ---------------------------------------------------------------------------


class TestSellerOrderUpdateStatusTransicoesValidas(SellerOrderStatusSetUpMixin):
    """Verifica que as transições permitidas funcionam corretamente."""

    def test_pending_para_confirmed(self):
        """PENDING → CONFIRMED deve ser aceito e salvo no banco."""
        self.http_client.force_login(self.seller_user)
        response = self.http_client.post(self.url_update, {'status': 'CONFIRMED'})
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)

    def test_confirmed_para_shipped(self):
        """CONFIRMED → SHIPPED deve ser aceito e salvo no banco."""
        self._set_order_status(Order.Status.CONFIRMED)
        self.http_client.force_login(self.seller_user)
        response = self.http_client.post(self.url_update, {'status': 'SHIPPED'})
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.SHIPPED)

    def test_shipped_para_delivered(self):
        """SHIPPED → DELIVERED deve ser aceito e salvo no banco."""
        self._set_order_status(Order.Status.SHIPPED)
        self.http_client.force_login(self.seller_user)
        response = self.http_client.post(self.url_update, {'status': 'DELIVERED'})
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.DELIVERED)

    def test_pending_para_cancelled(self):
        """PENDING → CANCELLED deve ser permitido."""
        response = self._post_status('CANCELLED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_confirmed_para_cancelled(self):
        """CONFIRMED → CANCELLED deve ser permitido."""
        self._set_order_status(Order.Status.CONFIRMED)
        response = self._post_status('CANCELLED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_shipped_para_cancelled(self):
        """SHIPPED → CANCELLED deve ser permitido."""
        self._set_order_status(Order.Status.SHIPPED)
        response = self._post_status('CANCELLED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_mensagem_de_sucesso_apos_atualizacao(self):
        """Após atualização válida, deve exibir mensagem de sucesso."""
        self.http_client.force_login(self.seller_user)
        response = self.http_client.post(
            self.url_update, {'status': 'CONFIRMED'}, follow=True
        )
        msgs = list(response.context['messages'])
        self.assertTrue(
            any('atualizado' in str(m).lower() for m in msgs),
            'Mensagem de sucesso deve conter a palavra "atualizado".',
        )


# ---------------------------------------------------------------------------
# 3. Transições inválidas (pular etapas)
# ---------------------------------------------------------------------------


class TestSellerOrderUpdateStatusPularEtapas(SellerOrderStatusSetUpMixin):
    """Verifica que pular etapas no ciclo de status é rejeitado."""

    def test_pending_nao_pode_ir_para_shipped(self):
        """PENDING → SHIPPED deve ser rejeitado (pula CONFIRMED)."""
        response = self._post_status('SHIPPED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.status,
            Order.Status.PENDING,
            'Status não deve ser alterado ao pular etapa.',
        )

    def test_pending_nao_pode_ir_para_delivered(self):
        """PENDING → DELIVERED deve ser rejeitado (pula CONFIRMED e SHIPPED)."""
        response = self._post_status('DELIVERED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING)

    def test_confirmed_nao_pode_ir_para_delivered(self):
        """CONFIRMED → DELIVERED deve ser rejeitado (pula SHIPPED)."""
        self._set_order_status(Order.Status.CONFIRMED)
        response = self._post_status('DELIVERED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)

    def test_mensagem_de_erro_ao_pular_etapa(self):
        """Ao tentar pular etapa, deve exibir mensagem de erro."""
        self.http_client.force_login(self.seller_user)
        response = self.http_client.post(
            self.url_update, {'status': 'SHIPPED'}, follow=True
        )
        msgs = list(response.context['messages'])
        self.assertTrue(
            any(m.tags == 'error' for m in msgs),
            'Deve exibir mensagem de erro ao pular etapa de status.',
        )


# ---------------------------------------------------------------------------
# 4. Transições inválidas (retroceder)
# ---------------------------------------------------------------------------


class TestSellerOrderUpdateStatusRetroceder(SellerOrderStatusSetUpMixin):
    """Verifica que retroceder o status é rejeitado."""

    def test_confirmed_nao_pode_voltar_para_pending(self):
        """CONFIRMED → PENDING deve ser rejeitado."""
        self._set_order_status(Order.Status.CONFIRMED)
        response = self._post_status('PENDING')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)

    def test_shipped_nao_pode_voltar_para_confirmed(self):
        """SHIPPED → CONFIRMED deve ser rejeitado."""
        self._set_order_status(Order.Status.SHIPPED)
        response = self._post_status('CONFIRMED')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.SHIPPED)

    def test_delivered_nao_permite_nenhuma_transicao(self):
        """DELIVERED é estado final — qualquer tentativa de mudança deve ser rejeitada."""
        self._set_order_status(Order.Status.DELIVERED)
        for novo_status in ['PENDING', 'CONFIRMED', 'SHIPPED', 'CANCELLED']:
            response = self._post_status(novo_status)
            self.assertRedirects(
                response, self.url_detail, fetch_redirect_response=False,
                msg_prefix=f'DELIVERED → {novo_status} deve ser rejeitado.',
            )
            self.order.refresh_from_db()
            self.assertEqual(
                self.order.status,
                Order.Status.DELIVERED,
                f'Status não deve mudar de DELIVERED para {novo_status}.',
            )

    def test_cancelled_nao_permite_nenhuma_transicao(self):
        """CANCELLED é estado final — qualquer tentativa de mudança deve ser rejeitada."""
        self._set_order_status(Order.Status.CANCELLED)
        for novo_status in ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED']:
            response = self._post_status(novo_status)
            self.assertRedirects(
                response, self.url_detail, fetch_redirect_response=False,
                msg_prefix=f'CANCELLED → {novo_status} deve ser rejeitado.',
            )
            self.order.refresh_from_db()
            self.assertEqual(
                self.order.status,
                Order.Status.CANCELLED,
                f'Status não deve mudar de CANCELLED para {novo_status}.',
            )


# ---------------------------------------------------------------------------
# 5. Status inválido (fora do enum)
# ---------------------------------------------------------------------------


class TestSellerOrderUpdateStatusInvalido(SellerOrderStatusSetUpMixin):
    """Verifica comportamento com valores de status fora do enum."""

    def test_status_invalido_rejeitado(self):
        """Valor arbitrário que não pertence ao enum deve ser rejeitado."""
        response = self._post_status('STATUS_INVENTADO')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING)

    def test_status_vazio_rejeitado(self):
        """POST com status vazio deve ser rejeitado."""
        response = self._post_status('')
        self.assertRedirects(response, self.url_detail, fetch_redirect_response=False)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING)

    def test_mensagem_de_erro_para_status_invalido(self):
        """Deve exibir mensagem de erro ao enviar status inválido."""
        self.http_client.force_login(self.seller_user)
        response = self.http_client.post(
            self.url_update, {'status': 'INVALIDO'}, follow=True
        )
        msgs = list(response.context['messages'])
        self.assertTrue(
            any(m.tags == 'error' for m in msgs),
            'Deve exibir mensagem de erro para status inválido.',
        )
