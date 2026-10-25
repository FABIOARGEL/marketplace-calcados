"""
Testes de integração para as views do app products.

Cobre:
    - Vendedor cria produto com sucesso (caminho feliz)
    - Cliente não acessa cadastro de produto (permissão)
    - Usuário não autenticado é redirecionado ao cadastro
    - Vendedor edita o próprio produto com sucesso
    - Vendedor não edita produto de outro vendedor (403/404)
    - Toggle de ativo/inativo funciona
    - Toggle requer POST (GET retorna 405)
    - Catálogo exibe apenas produtos ativos
    - Detalhe exibe informações completas do produto
    - Produto inativo retorna 404 no detalhe público

Executável via:
    python manage.py test tests.products
    python manage.py test tests.products.test_views
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.products.models import Category, Product, Stock

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers / Mixin
# ---------------------------------------------------------------------------


class ProductTestSetUpMixin(TestCase):
    """Cenário base reutilizável para testes de produtos.

    Cria:
        - seller_user: vendedor dono dos produtos de teste
        - outro_seller: segundo vendedor para testes de isolamento
        - client_user: cliente sem acesso às views de gestão
        - category: categoria de calçados
        - produto: produto ativo do seller_user (R$ 199,90, tamanho 42)
        - produto_inativo: produto inativo do seller_user
    """

    def setUp(self):
        self.http_client = Client()

        # Vendedor principal
        self.seller_user = User.objects.create_user(
            username='seller_products_test',
            email='seller@products.test',
            password='Senha@Forte123',
            first_name='Carlos',
            last_name='Vendedor',
            user_type=User.UserType.SELLER,
        )

        # Segundo vendedor (isolamento)
        self.outro_seller = User.objects.create_user(
            username='outro_seller_test',
            email='outro_seller@products.test',
            password='Senha@Forte123',
            first_name='Ana',
            last_name='Outra',
            user_type=User.UserType.SELLER,
        )

        # Cliente (sem permissão para gestão)
        self.client_user = User.objects.create_user(
            username='client_products_test',
            email='client@products.test',
            password='Senha@Forte123',
            first_name='Joao',
            last_name='Cliente',
            user_type=User.UserType.CLIENT,
        )

        # Categoria
        self.category = Category.objects.create(
            name='Tenis',
            slug='tenis',
        )

        # Produto ativo do seller_user
        self.produto = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name='Nike Air Force 1',
            description='Classico tenis urbano com amortecimento de espuma.',
            brand='Nike',
            price=Decimal('199.90'),
            is_active=True,
        )
        Stock.objects.create(
            product=self.produto,
            size='42',
            quantity=10,
        )

        # Produto inativo do seller_user
        self.produto_inativo = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name='Adidas Ultraboost Antigo',
            description='Modelo descontinuado.',
            brand='Adidas',
            price=Decimal('349.90'),
            is_active=False,
        )

        # Produto do outro vendedor
        self.produto_outro = Product.objects.create(
            seller=self.outro_seller,
            category=self.category,
            name='Vans Old Skool',
            description='Classico do skate street.',
            brand='Vans',
            price=Decimal('299.90'),
            is_active=True,
        )

        # URLs
        self.url_product_list = reverse('products:product-list')
        self.url_product_create = reverse('products:product-create')
        self.url_seller_list = reverse('products:seller-product-list')
        self.url_product_detail = reverse(
            'products:product-detail', kwargs={'pk': self.produto.pk}
        )
        self.url_produto_inativo_detail = reverse(
            'products:product-detail', kwargs={'pk': self.produto_inativo.pk}
        )
        self.url_edit_own = reverse(
            'products:product-edit', kwargs={'pk': self.produto.pk}
        )
        self.url_edit_outro = reverse(
            'products:product-edit', kwargs={'pk': self.produto_outro.pk}
        )
        self.url_toggle_own = reverse(
            'products:product-toggle-active', kwargs={'pk': self.produto.pk}
        )

    def _dados_produto_validos(self, **kwargs):
        """Retorna payload mínimo válido para criar/editar um produto via POST."""
        dados = {
            'name': 'Produto Teste',
            'description': 'Descricao completa do produto de teste.',
            'brand': 'MarcaTeste',
            'price': '129.90',
            'category': self.category.pk,
            # Stock inline formset — prefixo 'stock'
            'stock-TOTAL_FORMS': '1',
            'stock-INITIAL_FORMS': '0',
            'stock-MIN_NUM_FORMS': '0',
            'stock-MAX_NUM_FORMS': '30',
            'stock-0-size': '40',
            'stock-0-quantity': '5',
            # Image inline formset — prefixo 'images'
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '10',
        }
        dados.update(kwargs)
        return dados


# ---------------------------------------------------------------------------
# 1. Criação de produto — caminho feliz (vendedor)
# ---------------------------------------------------------------------------


class TestProductCreateAsSeller(ProductTestSetUpMixin):
    """Vendedor pode criar produto com sucesso."""

    def test_product_create_as_seller(self):
        """POST válido de vendedor cria produto e redireciona para meus-produtos."""
        self.http_client.force_login(self.seller_user)

        total_antes = Product.objects.count()
        dados = self._dados_produto_validos(name='Asics Gel Kayano')

        response = self.http_client.post(self.url_product_create, dados)

        self.assertEqual(
            Product.objects.count(),
            total_antes + 1,
            'Um novo produto deve ter sido criado.',
        )
        novo = Product.objects.filter(name='Asics Gel Kayano').first()
        self.assertIsNotNone(novo, 'Produto criado deve existir no banco.')
        self.assertEqual(novo.seller, self.seller_user, 'Produto deve pertencer ao seller_user.')
        self.assertRedirects(
            response,
            self.url_seller_list,
            fetch_redirect_response=False,
            msg_prefix='Após criar produto deve redirecionar para meus-produtos.',
        )

    def test_product_create_get_renders_form(self):
        """GET na tela de cadastro renderiza o formulário para o vendedor."""
        self.http_client.force_login(self.seller_user)

        response = self.http_client.get(self.url_product_create)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_form.html')
        self.assertIn('form', response.context)

    def test_product_create_sem_estoque_mostra_erro(self):
        """Cadastro sem nenhum tamanho de estoque não salva e exibe mensagem de erro."""
        self.http_client.force_login(self.seller_user)
        total_antes = Product.objects.count()

        dados = self._dados_produto_validos()
        # Sobrescreve o stock para que não haja nenhum tamanho preenchido
        dados['stock-0-size'] = ''
        dados['stock-0-quantity'] = '0'

        response = self.http_client.post(self.url_product_create, dados)

        self.assertEqual(
            Product.objects.count(),
            total_antes,
            'Nenhum produto deve ser criado sem estoque.',
        )
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# 2. Criação de produto — cliente não tem acesso
# ---------------------------------------------------------------------------


class TestProductCreateAsClientForbidden(ProductTestSetUpMixin):
    """Cliente não pode acessar nem submeter o cadastro de produtos."""

    def test_product_create_as_client_forbidden(self):
        """GET do cliente na tela de cadastro redireciona (acesso negado)."""
        self.http_client.force_login(self.client_user)

        response = self.http_client.get(self.url_product_create)

        # A view redireciona o cliente para 'home'
        self.assertRedirects(
            response,
            reverse('home'),
            fetch_redirect_response=False,
            msg_prefix='Cliente não deve acessar cadastro de produto.',
        )

    def test_product_create_post_as_client_forbidden(self):
        """POST do cliente não cria produto."""
        self.http_client.force_login(self.client_user)
        total_antes = Product.objects.count()

        dados = self._dados_produto_validos()
        self.http_client.post(self.url_product_create, dados)

        self.assertEqual(
            Product.objects.count(),
            total_antes,
            'Cliente não deve conseguir criar produto.',
        )

    def test_product_create_sem_autenticacao_redireciona(self):
        """Usuário não autenticado é redirecionado para a tela de login."""
        response = self.http_client.get(self.url_product_create)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_product_create}',
            fetch_redirect_response=False,
        )


# ---------------------------------------------------------------------------
# 3. Edição de produto — vendedor edita o próprio
# ---------------------------------------------------------------------------


class TestProductEditOwn(ProductTestSetUpMixin):
    """Vendedor consegue editar o próprio produto com sucesso."""

    def _dados_edicao(self, **kwargs):
        """Payload de edição com formsets pre-inicializados para produto existente."""
        stock_existente = self.produto.stock_items.first()
        dados = {
            'name': 'Nike Air Force 1 Editado',
            'description': 'Descricao atualizada com novos detalhes.',
            'brand': 'Nike',
            'price': '219.90',
            'category': self.category.pk,
            # Stock formset com o item existente
            'stock-TOTAL_FORMS': '1',
            'stock-INITIAL_FORMS': '1',
            'stock-MIN_NUM_FORMS': '0',
            'stock-MAX_NUM_FORMS': '30',
            'stock-0-id': str(stock_existente.pk),
            'stock-0-product': str(self.produto.pk),
            'stock-0-size': '42',
            'stock-0-quantity': '8',
            # Image formset vazio
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '10',
        }
        dados.update(kwargs)
        return dados

    def test_product_edit_own(self):
        """Vendedor edita o próprio produto e é redirecionado para meus-produtos."""
        self.http_client.force_login(self.seller_user)

        response = self.http_client.post(self.url_edit_own, self._dados_edicao())

        self.produto.refresh_from_db()
        self.assertEqual(
            self.produto.name,
            'Nike Air Force 1 Editado',
            'Nome do produto deve ter sido atualizado.',
        )
        self.assertEqual(
            self.produto.price,
            Decimal('219.90'),
            'Preço do produto deve ter sido atualizado.',
        )
        self.assertRedirects(
            response,
            self.url_seller_list,
            fetch_redirect_response=False,
        )

    def test_product_edit_own_get_renders_form(self):
        """GET na edição renderiza o formulário com dados do produto."""
        self.http_client.force_login(self.seller_user)

        response = self.http_client.get(self.url_edit_own)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_form.html')
        self.assertTrue(
            response.context.get('modo_edicao'),
            'Contexto deve indicar modo de edição.',
        )


# ---------------------------------------------------------------------------
# 4. Edição de produto — não edita produto de outro vendedor
# ---------------------------------------------------------------------------


class TestProductEditOtherSellerForbidden(ProductTestSetUpMixin):
    """Vendedor não consegue editar produto que não é seu."""

    def test_product_edit_other_seller_forbidden(self):
        """GET na edição de produto de outro vendedor retorna 404."""
        self.http_client.force_login(self.seller_user)

        response = self.http_client.get(self.url_edit_outro)

        self.assertEqual(
            response.status_code,
            404,
            'Editar produto de outro vendedor deve retornar 404.',
        )

    def test_product_edit_other_seller_post_forbidden(self):
        """POST na edição de produto de outro vendedor não altera o produto."""
        self.http_client.force_login(self.seller_user)

        nome_original = self.produto_outro.name

        dados = {
            'name': 'Nome Hackeado',
            'description': 'Descricao hackeada.',
            'brand': 'HackedBrand',
            'price': '1.00',
            'stock-TOTAL_FORMS': '1',
            'stock-INITIAL_FORMS': '0',
            'stock-MIN_NUM_FORMS': '0',
            'stock-MAX_NUM_FORMS': '30',
            'stock-0-size': '40',
            'stock-0-quantity': '1',
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '10',
        }
        self.http_client.post(self.url_edit_outro, dados)

        self.produto_outro.refresh_from_db()
        self.assertEqual(
            self.produto_outro.name,
            nome_original,
            'Produto de outro vendedor não deve ser alterado.',
        )

    def test_product_edit_sem_autenticacao_redireciona(self):
        """Usuário não autenticado que tenta editar produto é redirecionado para login."""
        response = self.http_client.get(self.url_edit_own)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_edit_own}',
            fetch_redirect_response=False,
        )


# ---------------------------------------------------------------------------
# 5. Toggle de ativo/inativo
# ---------------------------------------------------------------------------


class TestProductToggleActive(ProductTestSetUpMixin):
    """Toggle de ativo/inativo funciona corretamente via POST."""

    def test_product_toggle_active_desativa(self):
        """Produto ativo é desativado após o toggle."""
        self.http_client.force_login(self.seller_user)

        self.assertTrue(self.produto.is_active, 'Produto deve iniciar ativo.')

        response = self.http_client.post(self.url_toggle_own)

        self.produto.refresh_from_db()
        self.assertFalse(
            self.produto.is_active,
            'Produto deve ter sido desativado pelo toggle.',
        )
        self.assertRedirects(
            response,
            self.url_seller_list,
            fetch_redirect_response=False,
        )

    def test_product_toggle_active_reativa(self):
        """Produto inativo é reativado após o toggle."""
        self.http_client.force_login(self.seller_user)

        self.produto.is_active = False
        self.produto.save()

        self.http_client.post(self.url_toggle_own)

        self.produto.refresh_from_db()
        self.assertTrue(
            self.produto.is_active,
            'Produto deve ter sido reativado pelo toggle.',
        )

    def test_product_toggle_get_retorna_405(self):
        """GET no endpoint de toggle retorna 405 (apenas POST permitido)."""
        self.http_client.force_login(self.seller_user)

        response = self.http_client.get(self.url_toggle_own)

        self.assertEqual(
            response.status_code,
            405,
            'GET no toggle deve retornar 405 Method Not Allowed.',
        )

    def test_product_toggle_outro_seller_retorna_404(self):
        """Toggle em produto de outro vendedor retorna 404."""
        self.http_client.force_login(self.seller_user)

        url_toggle_outro = reverse(
            'products:product-toggle-active', kwargs={'pk': self.produto_outro.pk}
        )
        response = self.http_client.post(url_toggle_outro)

        self.assertEqual(
            response.status_code,
            404,
            'Toggle em produto de outro vendedor deve retornar 404.',
        )

    def test_product_toggle_sem_autenticacao_redireciona(self):
        """Usuário não autenticado é redirecionado para login ao tentar toggle."""
        response = self.http_client.post(self.url_toggle_own)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_toggle_own}',
            fetch_redirect_response=False,
        )


# ---------------------------------------------------------------------------
# 6. Catálogo público — exibe apenas produtos ativos
# ---------------------------------------------------------------------------


class TestCatalogShowsActiveOnly(ProductTestSetUpMixin):
    """O catálogo público exibe apenas produtos com is_active=True."""

    def test_catalog_shows_active_only(self):
        """Catálogo lista produto ativo e omite produto inativo."""
        response = self.http_client.get(self.url_product_list)

        self.assertEqual(response.status_code, 200)

        produtos_na_pagina = list(response.context['page_obj'])
        ids = [p.pk for p in produtos_na_pagina]

        self.assertIn(
            self.produto.pk,
            ids,
            'Produto ativo deve aparecer no catálogo.',
        )
        self.assertNotIn(
            self.produto_inativo.pk,
            ids,
            'Produto inativo não deve aparecer no catálogo.',
        )

    def test_catalog_accessible_without_login(self):
        """Catálogo é público: não exige autenticação."""
        response = self.http_client.get(self.url_product_list)
        self.assertEqual(response.status_code, 200)

    def test_catalog_search_filters_active_products(self):
        """Busca por nome retorna apenas produtos ativos que correspondam ao termo."""
        response = self.http_client.get(
            self.url_product_list, {'q': 'Adidas Ultraboost Antigo'}
        )

        self.assertEqual(response.status_code, 200)
        produtos = list(response.context['page_obj'])
        ids = [p.pk for p in produtos]

        self.assertNotIn(
            self.produto_inativo.pk,
            ids,
            'Busca não deve retornar produto inativo.',
        )

    def test_catalog_template_used(self):
        """Catálogo usa o template correto."""
        response = self.http_client.get(self.url_product_list)
        self.assertTemplateUsed(response, 'products/product_list.html')


# ---------------------------------------------------------------------------
# 7. Detalhe de produto — exibe informações completas
# ---------------------------------------------------------------------------


class TestProductDetailShowsInfo(ProductTestSetUpMixin):
    """Página de detalhe exibe todas as informações do produto."""

    def test_product_detail_shows_info(self):
        """Detalhe exibe nome, marca, preço e estoque disponível."""
        response = self.http_client.get(self.url_product_detail)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')

        # Verifica os dados no contexto
        produto_ctx = response.context['produto']
        self.assertEqual(produto_ctx.pk, self.produto.pk)
        self.assertEqual(produto_ctx.name, self.produto.name)
        self.assertEqual(produto_ctx.brand, self.produto.brand)
        self.assertEqual(produto_ctx.price, self.produto.price)

    def test_product_detail_stock_items_in_context(self):
        """Detalhe inclui itens de estoque disponíveis no contexto."""
        response = self.http_client.get(self.url_product_detail)

        self.assertIn('stock_items', response.context)
        self.assertIn('has_stock', response.context)
        self.assertTrue(
            response.context['has_stock'],
            'Produto com estoque deve ter has_stock=True.',
        )

    def test_product_detail_accessible_without_login(self):
        """Detalhe do produto é público: não exige autenticação."""
        response = self.http_client.get(self.url_product_detail)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_contains_product_name(self):
        """O conteúdo HTML do detalhe deve conter o nome do produto."""
        response = self.http_client.get(self.url_product_detail)
        self.assertContains(response, self.produto.name)


# ---------------------------------------------------------------------------
# 8. Detalhe de produto inativo retorna 404
# ---------------------------------------------------------------------------


class TestProductDetailInactive404(ProductTestSetUpMixin):
    """Produto inativo retorna 404 na página de detalhe pública."""

    def test_product_detail_inactive_404(self):
        """GET no detalhe de produto inativo retorna HTTP 404."""
        response = self.http_client.get(self.url_produto_inativo_detail)

        self.assertEqual(
            response.status_code,
            404,
            'Detalhe de produto inativo deve retornar 404.',
        )

    def test_product_detail_active_returns_200(self):
        """GET no detalhe de produto ativo retorna HTTP 200."""
        response = self.http_client.get(self.url_product_detail)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_recem_desativado_retorna_404(self):
        """Produto recém desativado deve retornar 404 imediatamente."""
        self.produto.is_active = False
        self.produto.save()

        response = self.http_client.get(self.url_product_detail)

        self.assertEqual(
            response.status_code,
            404,
            'Produto recém desativado deve retornar 404 no detalhe público.',
        )
