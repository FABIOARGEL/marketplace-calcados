"""
Testes do app orders.

Cobre os fluxos de checkout, confirmação de pedido (order_confirm) e
página de sucesso (order_success) de acordo com os requisitos:
- RF15: Checkout com seleção de endereço e cálculo de frete
- RF16: Criação de OrderItem com snapshot de preço
- RF17: Criação de Order com endereço, valores e status de pagamento simulado
- RF18: Desconto atômico de estoque e limpeza do carrinho
- RF19: Exibição da página de confirmação de pedido
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product, Stock
from apps.users.models import Address

User = get_user_model()


class OrderProcessTests(TestCase):
    def setUp(self):
        # Usuário cliente
        self.client_user = User.objects.create_user(
            username='cliente@teste.com',
            email='cliente@teste.com',
            password='senha-teste-123',
            user_type=User.UserType.CLIENT,
        )

        # Outro usuário para testes de isolamento
        self.other_user = User.objects.create_user(
            username='outro@teste.com',
            email='outro@teste.com',
            password='senha-teste-123',
            user_type=User.UserType.CLIENT,
        )

        # Vendedor
        self.seller = User.objects.create_user(
            username='vendedor@teste.com',
            email='vendedor@teste.com',
            password='senha-teste-123',
            first_name='Vendedor',
            user_type=User.UserType.SELLER,
        )
        self.seller_profile = self.seller.seller_profile
        self.seller_profile.shipping_distance_km = Decimal('10.00')
        self.seller_profile.shipping_rate_per_km = Decimal('2.50')
        self.seller_profile.save()

        # Endereço do cliente
        self.address = Address.objects.create(
            user=self.client_user,
            nickname='Casa',
            recipient_name='Cliente Teste',
            zip_code='01001-000',
            street='Praça da Sé',
            number='100',
            neighborhood='Centro',
            city='São Paulo',
            state='SP',
            is_default=True,
        )

        # Endereço de outro usuário
        self.other_address = Address.objects.create(
            user=self.other_user,
            nickname='Outra Casa',
            recipient_name='Outro Usuário',
            zip_code='20000-000',
            street='Av Rio Branco',
            number='1',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
        )

        # Categoria e Produto
        self.category = Category.objects.create(
            name='Tênis Streetwear',
            slug='tenis-streetwear',
        )
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Dunk Low Retro',
            description='Tênis clássico streetwear',
            brand='Nike',
            price=Decimal('600.00'),
            is_active=True,
        )

        # Estoque
        self.stock_41 = Stock.objects.create(
            product=self.product,
            size='41',
            quantity=10,
        )

        # Carrinho do cliente com 2 unidades
        self.cart = Cart.objects.create(user=self.client_user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            size='41',
            quantity=2,
        )

        self.confirm_url = reverse('orders:order-confirm')

    def test_order_confirm_requires_login(self):
        """order_confirm deve redirecionar para login se usuário anônimo."""
        response = self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_order_confirm_requires_post(self):
        """order_confirm só deve aceitar POST (405 em GET)."""
        self.client.force_login(self.client_user)
        response = self.client.get(self.confirm_url)
        self.assertEqual(response.status_code, 405)

    def test_order_confirm_missing_address_redirects_with_error(self):
        """Se address_id não for informado, redireciona para checkout."""
        self.client.force_login(self.client_user)
        response = self.client.post(self.confirm_url, {
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        self.assertRedirects(response, reverse('orders:checkout'))

    def test_order_confirm_missing_payment_method_redirects_with_error(self):
        """Se payment_method não for informado, redireciona para checkout."""
        self.client.force_login(self.client_user)
        response = self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
        })
        self.assertRedirects(response, reverse('orders:checkout'))

    def test_order_confirm_invalid_payment_method_redirects_with_error(self):
        """Se payment_method for inválido, redireciona para checkout."""
        self.client.force_login(self.client_user)
        response = self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': 'BITCOIN_REAL',
        })
        self.assertRedirects(response, reverse('orders:checkout'))

    def test_order_confirm_address_belonging_to_another_user_returns_404(self):
        """Cliente não pode usar endereço de outro usuário."""
        self.client.force_login(self.client_user)
        response = self.client.post(self.confirm_url, {
            'address_id': self.other_address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        self.assertEqual(response.status_code, 404)

    def test_order_confirm_empty_cart_redirects_to_cart_detail(self):
        """Se o carrinho estiver vazio, redireciona para a página do carrinho."""
        self.client.force_login(self.client_user)
        self.cart.items.all().delete()

        response = self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        self.assertRedirects(response, reverse('cart:cart-detail'))

    def test_order_confirm_insufficient_stock_prevents_order_creation(self):
        """Se a quantidade em estoque for insuficiente, não cria pedido nem altera estoque."""
        self.client.force_login(self.client_user)
        # Reduz estoque para menos do que o carrinho (carrinho tem 2, estoque passa para 1)
        self.stock_41.quantity = 1
        self.stock_41.save()

        response = self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })

        self.assertRedirects(response, reverse('orders:checkout'))
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        # Estoque não foi alterado
        self.stock_41.refresh_from_db()
        self.assertEqual(self.stock_41.quantity, 1)
        # Carrinho continua intacto
        self.assertEqual(self.cart.items.count(), 1)

    def test_order_confirm_success_flow(self):
        """Testa o fluxo completo de sucesso:

        1. Cria Order com dados corretos e valores snapshot
        2. Cria OrderItems com unit_price = product.price (snapshot)
        3. Desconta estoque (Stock.quantity -= item.quantity)
        4. Limpa itens do carrinho
        5. Redireciona para order-success
        """
        self.client.force_login(self.client_user)

        estoque_inicial = self.stock_41.quantity  # 10
        qtd_comprada = self.cart_item.quantity     # 2

        response = self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.CREDIT_CARD_SIM,
        })

        # 1. Verifica criação do Order
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.client_user)
        self.assertEqual(order.shipping_address, self.address)
        self.assertEqual(order.payment_method, Order.PaymentMethod.CREDIT_CARD_SIM)
        self.assertEqual(order.payment_status, Order.PaymentStatus.APPROVED)
        self.assertEqual(order.status, Order.Status.CONFIRMED)

        # 2. Valores financeiros e frete
        # Subtotal: 2 * 600.00 = 1200.00
        # Frete: 10 km * 2.50 = 25.00
        # Total: 1225.00
        self.assertEqual(order.subtotal, Decimal('1200.00'))
        self.assertEqual(order.shipping_cost, Decimal('25.00'))
        self.assertEqual(order.total, Decimal('1225.00'))

        # 3. Verifica OrderItems e snapshot de preço
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.size, '41')
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal('600.00'))
        self.assertEqual(item.subtotal, Decimal('1200.00'))

        # Modifica preço do produto no catálogo para testar se snapshot permanece
        self.product.price = Decimal('999.00')
        self.product.save()
        item.refresh_from_db()
        self.assertEqual(item.unit_price, Decimal('600.00'))

        # 4. Verifica desconto de estoque
        self.stock_41.refresh_from_db()
        self.assertEqual(self.stock_41.quantity, estoque_inicial - qtd_comprada)  # 8

        # 5. Verifica carrinho limpo
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)

        # 6. Redirecionamento para a tela de sucesso
        success_url = reverse('orders:order-success', kwargs={'pk': order.pk})
        self.assertRedirects(response, success_url)

    def test_order_success_view(self):
        """A view order_success deve exibir detalhes do pedido para o dono."""
        self.client.force_login(self.client_user)

        # Confirma um pedido
        self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        order = Order.objects.first()

        success_url = reverse('orders:order-success', kwargs={'pk': order.pk})
        response = self.client.get(success_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_success.html')
        self.assertContains(response, f'Pedido #{order.pk}')
        self.assertContains(response, 'Dunk Low Retro')
        self.assertContains(response, 'Pagamento aprovado (simulação acadêmica)')
        self.assertContains(response, 'Praça da Sé, 100')

    def test_order_success_forbidden_for_other_user(self):
        """Usuário não pode ver a página de sucesso do pedido de outro usuário (404)."""
        self.client.force_login(self.client_user)

        self.client.post(self.confirm_url, {
            'address_id': self.address.pk,
            'payment_method': Order.PaymentMethod.PIX_SIM,
        })
        order = Order.objects.first()

        # Tenta acessar com outro usuário
        self.client.force_login(self.other_user)
        success_url = reverse('orders:order-success', kwargs={'pk': order.pk})
        response = self.client.get(success_url)

        self.assertEqual(response.status_code, 404)
