"""
Testes da página inicial (Home) — Marketplace de Calçados.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class HomePageTest(TestCase):
    """Testes da landing page / home do marketplace."""

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
        """Acessar '/' deve retornar 200 e utilizar home.html e base.html."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_contains_hero_section(self):
        """A home deve conter a seção hero com título e botão de ação."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Calçados que")
        self.assertContains(response, "hero__btn--primary")
        self.assertContains(response, "Explorar produtos")

    def test_home_contains_featured_products_placeholder(self):
        """A home deve exibir a seção de produtos em destaque (placeholder)."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Produtos em destaque")
        self.assertContains(response, "product-placeholder")
        self.assertContains(response, "Sprint 3")

    def test_home_contains_categories_section(self):
        """A home deve exibir as categorias em destaque."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Categorias")
        self.assertContains(response, "category-card")
        self.assertContains(response, "Tênis")
        self.assertContains(response, "Botas")

    def test_home_unauthenticated_state(self):
        """Quando não autenticado, deve exibir links de login e cadastro."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Login")
        self.assertContains(response, "Cadastro")
        self.assertContains(response, "Criar conta grátis")

    def test_home_authenticated_state(self):
        """Quando autenticado, deve exibir o nome do usuário e botão de logout."""
        self.client.login(username="cliente@teste.com", password="SenhaForte@123")
        response = self.client.get(self.home_url)
        self.assertContains(response, "João Silva")
        self.assertContains(response, "Sair")
        self.assertNotContains(response, "Criar conta grátis")

    def test_redirect_urls_configured(self):
        """LOGIN_REDIRECT_URL e LOGOUT_REDIRECT_URL devem apontar para a home."""
        self.assertIn(settings.LOGIN_REDIRECT_URL, ["/", "home"])
        self.assertIn(settings.LOGOUT_REDIRECT_URL, ["/", "home"])