"""
Testes unitários e de integração do app cart.

Cobre os requisitos:
- RF11: Adicionar calçado ao carrinho com tamanho e quantidade
- RF12: Atualizar quantidade se o item (produto + tamanho) já estiver no carrinho
- RF13: Validação de estoque disponível por tamanho
- RF14: Cálculo de subtotal do item e total do carrinho
- Controle de acesso (@login_required e @require_POST)
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cart.models import Cart, CartItem
from apps.products.models import Category, Product, Stock

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        # Usuário comprador
        self.buyer = User.objects.create_user(
            username='comprador',
            email='comprador@teste.com',
            password='senha-teste-123',
            user_type='BUYER',
        )

        # Vendedor e produto
        self.seller = User.objects.create_user(
            username='vendedor',
            email='vendedor@teste.com',
            password='senha-teste-123',
            user_type='SELLER',
        )

        self.category = Category.objects.create(
            name='Tênis Esportivo',
            slug='tenis-esportivo',
        )

        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Air Zoom Pegasus',
            description='Tênis de corrida amortecido',
            brand='Nike',
            price=Decimal('500.00'),
            is_active=True,
        )

        # Estoque com tamanhos variados
        self.stock_40 = Stock.objects.create(
            product=self.product,
            size='40',
            quantity=5,
        )
        self.stock_42 = Stock.objects.create(
            product=self.product,
            size='42',
            quantity=0,  # Esgotado
        )

        self.add_url = reverse('cart:cart-add')
        self.detail_url = reverse('cart:cart-detail')

        self.product_url = reverse('products:product-detail', args=[self.product.pk])

    def login_buyer(self):
        self.client.login(
            email='comprador@teste.com',
            password='senha-teste-123',
        )

    def test_unauthenticated_user_cannot_add_to_cart(self):
        """Usuário anônimo é redirecionado para a página de login."""
        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 1},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/', response.url)

    def test_cart_add_requires_post(self):
        """GET em /carrinho/adicionar/ deve retornar 405 Method Not Allowed."""
        self.login_buyer()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 405)

    def test_add_to_cart_success_new_item(self):
        """Adiciona item inexistente: cria Cart e CartItem com a quantidade solicitada."""
        self.login_buyer()
        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 2},
        )
        self.assertRedirects(response, self.detail_url)

        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(cart.items.count(), 1)

        item = cart.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.size, '40')
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.subtotal, Decimal('1000.00'))
        self.assertEqual(cart.total, Decimal('1000.00'))

    def test_add_to_cart_increments_existing_item(self):
        """Mesmo produto + tamanho atualiza a quantidade (não duplica CartItem)."""
        self.login_buyer()

        # Primeiro envio: adiciona 2 unidades
        self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 2},
        )

        # Segundo envio: adiciona mais 1 unidade do mesmo tamanho
        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 1},
        )
        self.assertRedirects(response, self.detail_url)

        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(cart.items.count(), 1)

        item = cart.items.first()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(cart.total, Decimal('1500.00'))

    def test_cannot_add_item_with_insufficient_stock(self):
        """Não permite adicionar quantidade maior do que o estoque disponível."""
        self.login_buyer()

        # Tenta pedir 10 quando só há 5
        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 10},
            HTTP_REFERER=self.product_url,
        )
        self.assertRedirects(response, self.product_url)
        self.assertFalse(CartItem.objects.filter(product=self.product).exists())

    def test_cannot_add_item_when_stock_is_zero(self):
        """Não permite adicionar item esgotado (estoque = 0)."""
        self.login_buyer()

        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '42', 'quantity': 1},
            HTTP_REFERER=self.product_url,
        )
        self.assertRedirects(response, self.product_url)
        self.assertFalse(CartItem.objects.filter(product=self.product).exists())

    def test_accumulated_quantity_cannot_exceed_stock(self):
        """Não permite acumular no carrinho quantidade total superior ao estoque."""
        self.login_buyer()

        # Adiciona 4 unidades (estoque total = 5)
        self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 4},
        )

        # Tenta adicionar mais 2 unidades (4 + 2 = 6 > 5)
        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '40', 'quantity': 2},
            HTTP_REFERER=self.product_url,
        )
        self.assertRedirects(response, self.product_url)

        item = CartItem.objects.get(product=self.product, size='40')
        self.assertEqual(item.quantity, 4)

    def test_cannot_add_nonexistent_size(self):
        """Tentativa de adicionar tamanho que não consta no estoque retorna erro."""
        self.login_buyer()

        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '46', 'quantity': 1},
            HTTP_REFERER=self.product_url,
        )
        self.assertRedirects(response, self.product_url)
        self.assertFalse(CartItem.objects.exists())

    def test_invalid_parameters_rejects_gracefully(self):
        """Parâmetros faltantes ou quantidade negativa não criam itens."""
        self.login_buyer()

        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'size': '', 'quantity': -1},
            HTTP_REFERER=self.product_url,
        )
        self.assertRedirects(response, self.product_url)
        self.assertFalse(CartItem.objects.exists())

    def test_cart_detail_view_authenticated(self):
        """Visualização do carrinho renderiza template correto com totais."""
        self.login_buyer()

        # Cria carrinho com 1 item
        cart = Cart.objects.create(user=self.buyer)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            size='40',
            quantity=2,
        )

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')
        self.assertContains(response, 'Air Zoom Pegasus')
        self.assertContains(response, 'Tamanho: <strong>40</strong>')
        self.assertEqual(response.context['total'], Decimal('1000.00'))

    def test_cart_detail_view_empty(self):
        """Visualização de carrinho vazio exibe mensagem informativa."""
        self.login_buyer()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seu carrinho está vazio')
