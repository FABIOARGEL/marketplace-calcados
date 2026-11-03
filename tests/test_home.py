
"""
Testes da página inicial (Home) — Marketplace de Calçados.

A home foi unificada com o catálogo de produtos (apps.products.views.product_list).
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class HomePageTest(TestCase):
    """Testes da landing page / catálogo inicial do marketplace."""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home")
        self.user = User.objects.create_user(
            username="cliente@teste.com",
            email="cliente@teste.com",
            password="SenhaForte@123",
            first_name="João",
            last_name="Silva",
            user_type=User.UserType.CLIENT,
        )

    def test_home_url_resolves_to_root(self):
        """A URL reversa 'home' deve resolver para '/'."""
        self.assertEqual(self.home_url, "/")

    def test_home_status_code_and_templates(self):
        """Acessar '/' deve retornar 200 e utilizar product_list.html e base.html."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_list.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_contains_search_and_catalog(self):
        """A home deve conter o cabeçalho do catálogo e campo de busca."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Catálogo")
        self.assertContains(response, "catalog-search")
        self.assertContains(response, "Buscar calçados")

    def test_home_contains_filters_sidebar(self):
        """A home deve exibir o painel de filtros do catálogo."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "catalog-sidebar")
        self.assertContains(response, "Filtros")

    def test_home_unauthenticated_state(self):
        """Quando não autenticado, deve exibir links de login e cadastro no header."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Login")
        self.assertContains(response, "Cadastro")

    def test_home_authenticated_state(self):
        """Quando autenticado, deve exibir o primeiro nome do usuário e botão de logout."""
        self.client.login(username="cliente@teste.com", password="SenhaForte@123")
        response = self.client.get(self.home_url)
        self.assertContains(response, "João")
        self.assertContains(response, "Sair")
        self.assertNotContains(response, 'href="/usuarios/login/"')

    def test_redirect_urls_configured(self):
        """LOGIN_REDIRECT_URL e LOGOUT_REDIRECT_URL devem apontar para a home."""
        self.assertIn(settings.LOGIN_REDIRECT_URL, ["/", "home"])
        self.assertIn(settings.LOGOUT_REDIRECT_URL, ["/", "home"])
