"""
Testes de integração para busca e filtros do catálogo de produtos.

Cobre:
    - Busca por nome encontra produto ativo
    - Busca sem resultados retorna lista vazia
    - Filtro por categoria exibe apenas produtos da categoria
    - Filtro por faixa de preço (preco_min / preco_max)
    - Filtros combinados (categoria + faixa de preço, texto + categoria)

Executável via:
    python manage.py test tests.products.test_search_filters
    python manage.py test tests.products
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.products.models import Category, Product, Stock

User = get_user_model()


# ---------------------------------------------------------------------------
# Mixin base — reutilizado por todas as classes de busca/filtro
# ---------------------------------------------------------------------------


class SearchFilterSetUpMixin(TestCase):
    """Cenário base para testes de busca e filtros do catálogo.

    Cria:
        - seller_user: vendedor dono dos produtos
        - cat_tenis: categoria 'Tenis'
        - cat_bota: categoria 'Bota'
        - produto_nike: tenis Nike, R$ 199,90 (ativo, tamanho 42)
        - produto_adidas: tenis Adidas, R$ 349,90 (ativo, tamanho 40)
        - produto_bota: bota generica, R$ 450,00 (ativo, tamanho 38)
        - produto_inativo: produto inativo (nao deve aparecer em nenhum filtro)
    """

    def setUp(self):
        self.http_client = Client()
        self.url_catalog = reverse('products:product-list')

        # Vendedor
        self.seller_user = User.objects.create_user(
            username='seller_search_test',
            email='seller@search.test',
            password='Senha@Forte123',
            first_name='Loja',
            last_name='Search',
            user_type=User.UserType.SELLER,
        )

        # Categorias
        self.cat_tenis = Category.objects.create(name='Tenis Search', slug='tenis-search')
        self.cat_bota = Category.objects.create(name='Bota Search', slug='bota-search')

        # Produto 1 — Nike Air Max (ativo)
        self.produto_nike = Product.objects.create(
            seller=self.seller_user,
            category=self.cat_tenis,
            name='Nike Air Max',
            description='Tenis esportivo de alta performance da Nike.',
            brand='Nike',
            price=Decimal('199.90'),
            is_active=True,
        )
        Stock.objects.create(product=self.produto_nike, size='42', quantity=10)

        # Produto 2 — Adidas Ultraboost (ativo)
        self.produto_adidas = Product.objects.create(
            seller=self.seller_user,
            category=self.cat_tenis,
            name='Adidas Ultraboost',
            description='Tenis de corrida com amortecimento superior da Adidas.',
            brand='Adidas',
            price=Decimal('349.90'),
            is_active=True,
        )
        Stock.objects.create(product=self.produto_adidas, size='40', quantity=5)

        # Produto 3 — Bota Couro (ativo, outra categoria, preco alto)
        self.produto_bota = Product.objects.create(
            seller=self.seller_user,
            category=self.cat_bota,
            name='Bota Couro Classica',
            description='Bota de couro genuino para o dia a dia.',
            brand='Reserva',
            price=Decimal('450.00'),
            is_active=True,
        )
        Stock.objects.create(product=self.produto_bota, size='38', quantity=3)

        # Produto 4 — inativo (nao deve aparecer em nenhum resultado)
        self.produto_inativo = Product.objects.create(
            seller=self.seller_user,
            category=self.cat_tenis,
            name='Nike Antigo Inativo',
            description='Modelo descontinuado.',
            brand='Nike',
            price=Decimal('99.90'),
            is_active=False,
        )


# ---------------------------------------------------------------------------
# 1. Busca por nome — encontra produto pelo nome
# ---------------------------------------------------------------------------


class TestSearchByName(SearchFilterSetUpMixin):
    """Busca por termo presente no nome do produto retorna o produto correto."""

    def test_search_by_name(self):
        """Busca por 'Air Max' retorna apenas o produto Nike Air Max."""
        response = self.http_client.get(self.url_catalog, {'q': 'Air Max'})

        self.assertEqual(response.status_code, 200)

        produtos = list(response.context['page_obj'])
        ids = [p.pk for p in produtos]

        self.assertIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max deve aparecer na busca por "Air Max".',
        )
        self.assertNotIn(
            self.produto_adidas.pk,
            ids,
            'Adidas Ultraboost nao deve aparecer na busca por "Air Max".',
        )

    def test_search_by_partial_name(self):
        """Busca parcial por 'ultra' (case-insensitive) encontra Adidas Ultraboost."""
        response = self.http_client.get(self.url_catalog, {'q': 'ultra'})

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]
        self.assertIn(
            self.produto_adidas.pk,
            ids,
            'Adidas Ultraboost deve aparecer na busca parcial por "ultra".',
        )

    def test_search_does_not_return_inactive(self):
        """Busca por termo presente em produto inativo nao o retorna."""
        response = self.http_client.get(self.url_catalog, {'q': 'Nike Antigo Inativo'})

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]
        self.assertNotIn(
            self.produto_inativo.pk,
            ids,
            'Produto inativo nao deve aparecer nos resultados da busca.',
        )


# ---------------------------------------------------------------------------
# 2. Busca sem resultados
# ---------------------------------------------------------------------------


class TestSearchNoResults(SearchFilterSetUpMixin):
    """Busca por termo inexistente retorna lista vazia."""

    def test_search_no_results(self):
        """Busca por 'xyzprodutoinexistente' nao retorna nenhum produto."""
        response = self.http_client.get(
            self.url_catalog, {'q': 'xyzprodutoinexistente'}
        )

        self.assertEqual(response.status_code, 200)

        produtos = list(response.context['page_obj'])
        self.assertEqual(
            len(produtos),
            0,
            'Busca por termo inexistente deve retornar lista vazia.',
        )

    def test_search_no_results_total_count_zero(self):
        """total_count deve ser 0 quando nao ha resultados."""
        response = self.http_client.get(
            self.url_catalog, {'q': 'termoquenaoexiste99999'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['total_count'],
            0,
            'total_count deve ser 0 quando nenhum produto corresponde a busca.',
        )


# ---------------------------------------------------------------------------
# 3. Filtro por categoria
# ---------------------------------------------------------------------------


class TestFilterByCategory(SearchFilterSetUpMixin):
    """Filtro por categoria exibe apenas produtos daquela categoria."""

    def test_filter_by_category(self):
        """Filtrando pela categoria 'tenis-search' exibe tenis e oculta bota."""
        response = self.http_client.get(
            self.url_catalog, {'categoria': self.cat_tenis.slug}
        )

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]

        self.assertIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max deve aparecer ao filtrar por Tenis.',
        )
        self.assertIn(
            self.produto_adidas.pk,
            ids,
            'Adidas Ultraboost deve aparecer ao filtrar por Tenis.',
        )
        self.assertNotIn(
            self.produto_bota.pk,
            ids,
            'Bota Couro nao deve aparecer ao filtrar por Tenis.',
        )

    def test_filter_by_category_bota(self):
        """Filtrando pela categoria 'bota-search' exibe bota e oculta tenis."""
        response = self.http_client.get(
            self.url_catalog, {'categoria': self.cat_bota.slug}
        )

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]

        self.assertIn(
            self.produto_bota.pk,
            ids,
            'Bota Couro deve aparecer ao filtrar por Bota.',
        )
        self.assertNotIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max nao deve aparecer ao filtrar por Bota.',
        )

    def test_filter_by_nonexistent_category_returns_empty(self):
        """Filtrar por slug de categoria inexistente retorna lista vazia."""
        response = self.http_client.get(
            self.url_catalog, {'categoria': 'categoria-que-nao-existe'}
        )

        self.assertEqual(response.status_code, 200)
        produtos = list(response.context['page_obj'])
        self.assertEqual(
            len(produtos),
            0,
            'Categoria inexistente deve retornar lista vazia.',
        )


# ---------------------------------------------------------------------------
# 4. Filtro por faixa de preco
# ---------------------------------------------------------------------------


class TestFilterByPriceRange(SearchFilterSetUpMixin):
    """Filtros preco_min e preco_max aplicam a faixa de preco corretamente."""

    def test_filter_by_price_range(self):
        """Produtos com preco entre R$ 200,00 e R$ 400,00 sao retornados."""
        response = self.http_client.get(
            self.url_catalog, {'preco_min': '200', 'preco_max': '400'}
        )

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]

        # Adidas Ultraboost = R$349,90 → deve aparecer
        self.assertIn(
            self.produto_adidas.pk,
            ids,
            'Adidas Ultraboost (R$349,90) deve aparecer no filtro 200-400.',
        )
        # Nike Air Max = R$199,90 → abaixo do minimo
        self.assertNotIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max (R$199,90) nao deve aparecer no filtro 200-400.',
        )
        # Bota = R$450,00 → acima do maximo
        self.assertNotIn(
            self.produto_bota.pk,
            ids,
            'Bota Couro (R$450,00) nao deve aparecer no filtro 200-400.',
        )

    def test_filter_preco_min_only(self):
        """Filtro apenas com preco_min retorna produtos acima do minimo."""
        response = self.http_client.get(
            self.url_catalog, {'preco_min': '400'}
        )

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]

        self.assertIn(
            self.produto_bota.pk,
            ids,
            'Bota Couro (R$450,00) deve aparecer com preco_min=400.',
        )
        self.assertNotIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max (R$199,90) nao deve aparecer com preco_min=400.',
        )

    def test_filter_preco_max_only(self):
        """Filtro apenas com preco_max retorna produtos abaixo do maximo."""
        response = self.http_client.get(
            self.url_catalog, {'preco_max': '250'}
        )

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]

        self.assertIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max (R$199,90) deve aparecer com preco_max=250.',
        )
        self.assertNotIn(
            self.produto_bota.pk,
            ids,
            'Bota Couro (R$450,00) nao deve aparecer com preco_max=250.',
        )


# ---------------------------------------------------------------------------
# 5. Filtros combinados
# ---------------------------------------------------------------------------


class TestFilterCombined(SearchFilterSetUpMixin):
    """Multiplos filtros aplicados simultaneamente se comportam corretamente."""

    def test_filter_combined(self):
        """Categoria 'tenis-search' + preco_max=300 retorna apenas Nike Air Max."""
        response = self.http_client.get(
            self.url_catalog,
            {
                'categoria': self.cat_tenis.slug,
                'preco_max': '300',
            },
        )

        self.assertEqual(response.status_code, 200)

        ids = [p.pk for p in response.context['page_obj']]

        # Nike Air Max = R$199,90 na categoria tenis → deve aparecer
        self.assertIn(
            self.produto_nike.pk,
            ids,
            'Nike Air Max deve aparecer com categoria=tenis-search e preco_max=300.',
        )
        # Adidas Ultraboost = R$349,90 → acima do preco maximo
        self.assertNotIn(
            self.produto_adidas.pk,
            ids,
            'Adidas Ultraboost deve ser filtrado pelo preco_max=300.',
        )
        # Bota = outra categoria
        self.assertNotIn(
            self.produto_bota.pk,
            ids,
            'Bota Couro nao pertence a categoria tenis.',
        )

    def test_filter_combined_search_and_category(self):
        """Busca por texto + filtro de categoria combinados retornam intersecao."""
        response = self.http_client.get(
            self.url_catalog,
            {
                'q': 'Couro',
                'categoria': self.cat_tenis.slug,
            },
        )

        self.assertEqual(response.status_code, 200)

        # 'Couro' existe na Bota, mas Bota nao e Tenis → resultado vazio
        produtos = list(response.context['page_obj'])
        self.assertEqual(
            len(produtos),
            0,
            'Combinacao de busca "Couro" + categoria tenis deve retornar vazio.',
        )

    def test_filter_combined_all_active_flag(self):
        """filtros_ativos deve ser True quando algum filtro (exceto q) esta aplicado."""
        response = self.http_client.get(
            self.url_catalog,
            {'categoria': self.cat_tenis.slug},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.context['filtros_ativos'],
            'filtros_ativos deve ser True quando categoria esta selecionada.',
        )
