"""
Testes de integração para as views do app cart.

Cobre:
    - Adicionar produto ao carrinho (caminho feliz)
    - Adicionar mesmo produto+tamanho incrementa quantidade (nao duplica)
    - Adicionar quantidade acima do estoque disponivel e bloqueado
    - Atualizar quantidade de um item
    - Remover item do carrinho
    - Subtotal calculado corretamente pelo modelo
    - Acesso sem autenticacao redireciona para login

Executavel via:
    python manage.py test tests.cart.test_views
    python manage.py test tests.cart
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart, CartItem
from apps.products.models import Category, Product, Stock

User = get_user_model()


# ---------------------------------------------------------------------------
# Mixin base — cenario reutilizavel para todos os testes de carrinho
# ---------------------------------------------------------------------------


class CartTestSetUpMixin(TestCase):
    """Cenario base para testes de carrinho.

    Cria:
        - cliente_user: usuario do tipo CLIENT
        - outro_user: segundo cliente para isolamento
        - seller_user: vendedor dono do produto
        - category: categoria de calcados
        - produto: produto ativo com preco R$150,00
        - stock_42: estoque tamanho 42, quantidade 5
        - url_add: endpoint POST de adicionar ao carrinho
        - url_cart: endpoint GET do carrinho
    """

    def setUp(self):
        self.http_client = Client()

        # Usuarios
        self.cliente_user = User.objects.create_user(
            username='cliente_cart_test',
            email='cliente@cart.test',
            password='Senha@Forte123',
            first_name='Joao',
            last_name='Cliente',
            user_type=User.UserType.CLIENT,
        )

        self.outro_user = User.objects.create_user(
            username='outro_cart_test',
            email='outro@cart.test',
            password='Senha@Forte123',
            first_name='Maria',
            last_name='Outro',
            user_type=User.UserType.CLIENT,
        )

        self.seller_user = User.objects.create_user(
            username='seller_cart_test',
            email='seller@cart.test',
            password='Senha@Forte123',
            first_name='Loja',
            last_name='Seller',
            user_type=User.UserType.SELLER,
        )

        # Produto
        self.category = Category.objects.create(
            name='Tenis Cart', slug='tenis-cart'
        )
        self.produto = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name='Tenis Corrida XR',
            description='Tenis confortavel para corrida.',
            brand='SpeedBrand',
            price=Decimal('150.00'),
            is_active=True,
        )
        self.stock_42 = Stock.objects.create(
            product=self.produto, size='42', quantity=5
        )

        # URLs
        self.url_add = reverse('cart:cart-add')
        self.url_cart = reverse('cart:cart-detail')

    def _post_add(self, product_id=None, size='42', quantity=1):
        """Atalho para POST no endpoint de adicionar ao carrinho."""
        return self.http_client.post(
            self.url_add,
            {
                'product_id': str(product_id or self.produto.pk),
                'size': size,
                'quantity': str(quantity),
            },
        )

    def _get_cart(self):
        """Retorna o Cart do cliente_user, ou None se nao existir."""
        return Cart.objects.filter(user=self.cliente_user).first()

    def _get_cart_item(self, size='42'):
        """Retorna o CartItem do cliente_user para o produto+tamanho."""
        cart = self._get_cart()
        if cart is None:
            return None
        return CartItem.objects.filter(
            cart=cart, product=self.produto, size=size
        ).first()


# ---------------------------------------------------------------------------
# 1. Adicionar produto ao carrinho — caminho feliz
# ---------------------------------------------------------------------------


class TestAddToCart(CartTestSetUpMixin):
    """Adicionar produto ao carrinho cria Cart e CartItem corretamente."""

    def test_add_to_cart(self):
        """POST valido cria CartItem e redireciona para o carrinho."""
        self.http_client.force_login(self.cliente_user)

        response = self._post_add(quantity=1)

        # Deve redirecionar para o detalhe do carrinho
        self.assertRedirects(
            response,
            self.url_cart,
            fetch_redirect_response=False,
            msg_prefix='Adicionar ao carrinho deve redirecionar para cart-detail.',
        )

        # Cart criado automaticamente
        cart = self._get_cart()
        self.assertIsNotNone(cart, 'Cart deve ter sido criado para o usuario.')

        # CartItem criado
        item = self._get_cart_item()
        self.assertIsNotNone(item, 'CartItem deve ter sido criado.')
        self.assertEqual(item.quantity, 1, 'Quantidade do item deve ser 1.')
        self.assertEqual(item.size, '42', 'Tamanho do item deve ser "42".')

    def test_add_to_cart_creates_cart_automatically(self):
        """Cart e criado automaticamente na primeira adicao."""
        self.http_client.force_login(self.cliente_user)

        # Garante que nao ha cart previo
        self.assertIsNone(
            self._get_cart(), 'Nao deve haver Cart antes da primeira adicao.'
        )

        self._post_add()

        self.assertIsNotNone(
            self._get_cart(), 'Cart deve ser criado automaticamente.'
        )


# ---------------------------------------------------------------------------
# 2. Adicionar mesmo produto+tamanho incrementa quantidade
# ---------------------------------------------------------------------------


class TestAddSameProductUpdatesQty(CartTestSetUpMixin):
    """Adicionar o mesmo produto+tamanho novamente incrementa a quantidade."""

    def test_add_same_product_updates_qty(self):
        """Segunda adicao do mesmo produto+tamanho incrementa qty, nao duplica."""
        self.http_client.force_login(self.cliente_user)

        # Adiciona 1 unidade
        self._post_add(quantity=1)
        # Adiciona mais 2 unidades do mesmo produto+tamanho
        self._post_add(quantity=2)

        # Deve existir apenas 1 CartItem, com qty = 3
        cart = self._get_cart()
        total_items = CartItem.objects.filter(cart=cart, product=self.produto).count()
        self.assertEqual(
            total_items,
            1,
            'Nao deve criar CartItem duplicado para o mesmo produto+tamanho.',
        )

        item = self._get_cart_item()
        self.assertEqual(
            item.quantity,
            3,
            'Quantidade deve ser acumulada (1 + 2 = 3).',
        )

    def test_add_same_product_different_size_creates_new_item(self):
        """Mesmo produto com tamanho diferente cria um novo CartItem."""
        # Cria estoque para tamanho 40
        Stock.objects.create(product=self.produto, size='40', quantity=3)

        self.http_client.force_login(self.cliente_user)

        self._post_add(size='42', quantity=1)
        self._post_add(size='40', quantity=1)

        cart = self._get_cart()
        total_items = CartItem.objects.filter(cart=cart, product=self.produto).count()
        self.assertEqual(
            total_items,
            2,
            'Tamanhos diferentes devem gerar CartItems distintos.',
        )


# ---------------------------------------------------------------------------
# 3. Adicionar quantidade acima do estoque e bloqueado
# ---------------------------------------------------------------------------


class TestAddExceedsStock(CartTestSetUpMixin):
    """Adicionar quantidade maior que o estoque disponivel e bloqueado."""

    def test_add_exceeds_stock(self):
        """Quantidade solicitada maior que o estoque nao cria CartItem."""
        self.http_client.force_login(self.cliente_user)

        # Estoque e 5; tenta adicionar 10
        self._post_add(quantity=10)

        item = self._get_cart_item()
        self.assertIsNone(
            item,
            'CartItem nao deve ser criado quando a quantidade excede o estoque.',
        )

    def test_add_exceeds_stock_accumulated(self):
        """Acumular via multiplas adicoes acima do estoque e bloqueado."""
        self.http_client.force_login(self.cliente_user)

        # Adiciona 4 (dentro do estoque de 5)
        self._post_add(quantity=4)

        # Tenta adicionar mais 3 (total seria 7, acima do estoque)
        self._post_add(quantity=3)

        item = self._get_cart_item()
        self.assertIsNotNone(item, 'CartItem deve existir com a quantidade inicial.')
        self.assertEqual(
            item.quantity,
            4,
            'Quantidade nao deve ultrapassar o estoque disponivel (5).',
        )

    def test_add_to_esgotado_blocked(self):
        """Produto com estoque zerado nao pode ser adicionado ao carrinho."""
        self.stock_42.quantity = 0
        self.stock_42.save()

        self.http_client.force_login(self.cliente_user)

        self._post_add(quantity=1)

        item = self._get_cart_item()
        self.assertIsNone(
            item,
            'Produto esgotado nao deve ser adicionado ao carrinho.',
        )


# ---------------------------------------------------------------------------
# 4. Atualizar quantidade de um item
# ---------------------------------------------------------------------------


class TestUpdateQuantity(CartTestSetUpMixin):
    """Atualizar a quantidade de um CartItem existente."""

    def setUp(self):
        super().setUp()
        # Pre-cria Cart e CartItem para o cliente
        self.http_client.force_login(self.cliente_user)
        self._post_add(quantity=2)
        self.http_client.logout()

        self.cart = self._get_cart()
        self.item = self._get_cart_item()

    def test_update_quantity(self):
        """POST para cart-update com nova quantidade persiste a mudanca."""
        self.http_client.force_login(self.cliente_user)

        url_update = reverse('cart:cart-update', kwargs={'item_pk': self.item.pk})
        response = self.http_client.post(url_update, {'quantity': '3'})

        self.assertRedirects(
            response,
            self.url_cart,
            fetch_redirect_response=False,
        )

        self.item.refresh_from_db()
        self.assertEqual(
            self.item.quantity,
            3,
            'Quantidade do CartItem deve ser atualizada para 3.',
        )

    def test_update_quantity_above_stock_rejected(self):
        """Atualizar para quantidade acima do estoque e rejeitado."""
        self.http_client.force_login(self.cliente_user)

        url_update = reverse('cart:cart-update', kwargs={'item_pk': self.item.pk})
        # Estoque e 5; tenta atualizar para 99
        self.http_client.post(url_update, {'quantity': '99'})

        self.item.refresh_from_db()
        self.assertLessEqual(
            self.item.quantity,
            self.stock_42.quantity,
            'Quantidade nao deve ultrapassar o estoque disponivel.',
        )

    def test_update_quantity_zero_removes_item(self):
        """Atualizar para quantidade 0 remove automaticamente o CartItem."""
        self.http_client.force_login(self.cliente_user)

        url_update = reverse('cart:cart-update', kwargs={'item_pk': self.item.pk})
        self.http_client.post(url_update, {'quantity': '0'})

        item_exists = CartItem.objects.filter(pk=self.item.pk).exists()
        self.assertFalse(
            item_exists,
            'CartItem com quantidade 0 deve ser removido automaticamente.',
        )


# ---------------------------------------------------------------------------
# 5. Remover item do carrinho
# ---------------------------------------------------------------------------


class TestRemoveItem(CartTestSetUpMixin):
    """Remover um CartItem do carrinho via endpoint cart-remove."""

    def setUp(self):
        super().setUp()
        self.http_client.force_login(self.cliente_user)
        self._post_add(quantity=1)
        self.http_client.logout()

        self.cart = self._get_cart()
        self.item = self._get_cart_item()

    def test_remove_item(self):
        """POST para cart-remove exclui o CartItem e redireciona para o carrinho."""
        self.http_client.force_login(self.cliente_user)

        url_remove = reverse('cart:cart-remove', kwargs={'item_pk': self.item.pk})
        response = self.http_client.post(url_remove)

        self.assertRedirects(
            response,
            self.url_cart,
            fetch_redirect_response=False,
            msg_prefix='Remocao deve redirecionar para cart-detail.',
        )

        item_exists = CartItem.objects.filter(pk=self.item.pk).exists()
        self.assertFalse(
            item_exists,
            'CartItem deve ter sido removido do banco de dados.',
        )

    def test_remove_item_cart_becomes_empty(self):
        """Apos remover o unico item, o carrinho fica vazio."""
        self.http_client.force_login(self.cliente_user)

        url_remove = reverse('cart:cart-remove', kwargs={'item_pk': self.item.pk})
        self.http_client.post(url_remove)

        self.cart.refresh_from_db()
        self.assertEqual(
            self.cart.items.count(),
            0,
            'Carrinho deve estar vazio apos remocao do unico item.',
        )

    def test_remove_item_of_other_user_returns_404(self):
        """Tentar remover item de carrinho de outro usuario retorna 404."""
        # Cria cart e item para outro_user
        outro_cart = Cart.objects.create(user=self.outro_user)
        outro_item = CartItem.objects.create(
            cart=outro_cart, product=self.produto, size='42', quantity=1
        )

        self.http_client.force_login(self.cliente_user)

        url_remove = reverse('cart:cart-remove', kwargs={'item_pk': outro_item.pk})
        response = self.http_client.post(url_remove)

        self.assertEqual(
            response.status_code,
            404,
            'Remover item de outro usuario deve retornar 404.',
        )


# ---------------------------------------------------------------------------
# 6. Subtotal calculado corretamente
# ---------------------------------------------------------------------------


class TestCartSubtotal(CartTestSetUpMixin):
    """Subtotal e total do carrinho sao calculados corretamente."""

    def test_cart_subtotal(self):
        """Subtotal do CartItem = preco x quantidade."""
        self.http_client.force_login(self.cliente_user)
        self._post_add(quantity=3)

        item = self._get_cart_item()
        self.assertIsNotNone(item, 'CartItem deve existir.')

        subtotal_esperado = self.produto.price * item.quantity  # 150,00 x 3 = 450,00
        self.assertEqual(
            item.subtotal,
            subtotal_esperado,
            f'Subtotal esperado: R${subtotal_esperado}, obtido: R${item.subtotal}.',
        )

    def test_cart_total_equals_sum_of_items(self):
        """Total do Cart e a soma dos subtotais de todos os CartItems."""
        # Cria estoque para tamanho 40
        Stock.objects.create(product=self.produto, size='40', quantity=3)

        self.http_client.force_login(self.cliente_user)
        self._post_add(size='42', quantity=2)   # 2 x R$150,00 = R$300,00
        self._post_add(size='40', quantity=1)   # 1 x R$150,00 = R$150,00

        cart = self._get_cart()
        total_esperado = Decimal('450.00')

        self.assertEqual(
            cart.total,
            total_esperado,
            f'Total do carrinho deve ser R${total_esperado}, obtido: R${cart.total}.',
        )

    def test_cart_total_via_context(self):
        """Total exibido no contexto da view cart_detail bate com o modelo."""
        self.http_client.force_login(self.cliente_user)
        self._post_add(quantity=2)

        response = self.http_client.get(self.url_cart)

        self.assertEqual(response.status_code, 200)
        total_ctx = response.context['total']
        cart = self._get_cart()

        self.assertEqual(
            total_ctx,
            cart.total,
            'Total no contexto da view deve ser igual ao total do modelo.',
        )


# ---------------------------------------------------------------------------
# 7. Acesso sem autenticacao redireciona para login
# ---------------------------------------------------------------------------


class TestCartRequiresLogin(CartTestSetUpMixin):
    """Todas as views do carrinho requerem autenticacao."""

    def test_cart_requires_login_get(self):
        """GET em cart-detail sem autenticacao redireciona para login."""
        response = self.http_client.get(self.url_cart)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_cart}',
            fetch_redirect_response=False,
            msg_prefix='Acesso ao carrinho sem login deve redirecionar para login.',
        )

    def test_cart_add_requires_login(self):
        """POST em cart-add sem autenticacao redireciona para login."""
        response = self._post_add(quantity=1)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_add}',
            fetch_redirect_response=False,
            msg_prefix='Adicionar ao carrinho sem login deve redirecionar para login.',
        )

        # Nenhum Cart deve ter sido criado
        self.assertIsNone(
            self._get_cart(),
            'Nenhum Cart deve ser criado sem autenticacao.',
        )

    def test_cart_update_requires_login(self):
        """POST em cart-update sem autenticacao redireciona para login."""
        # Cria item direto no banco (sem passar pela view)
        cart = Cart.objects.create(user=self.cliente_user)
        item = CartItem.objects.create(
            cart=cart, product=self.produto, size='42', quantity=1
        )

        url_update = reverse('cart:cart-update', kwargs={'item_pk': item.pk})
        response = self.http_client.post(url_update, {'quantity': '2'})

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={url_update}',
            fetch_redirect_response=False,
        )

    def test_cart_remove_requires_login(self):
        """POST em cart-remove sem autenticacao redireciona para login."""
        cart = Cart.objects.create(user=self.cliente_user)
        item = CartItem.objects.create(
            cart=cart, product=self.produto, size='42', quantity=1
        )

        url_remove = reverse('cart:cart-remove', kwargs={'item_pk': item.pk})
        response = self.http_client.post(url_remove)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={url_remove}',
            fetch_redirect_response=False,
        )

        # Item nao deve ter sido removido
        self.assertTrue(
            CartItem.objects.filter(pk=item.pk).exists(),
            'CartItem nao deve ser removido sem autenticacao.',
        )
