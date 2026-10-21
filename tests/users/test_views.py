"""
Testes de views do app users.

Cobre os fluxos de cadastro, autenticação, logout e edição de perfil.
Executável via: python manage.py test tests.users.test_views
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.users.models import SellerProfile

User = get_user_model()


class UserViewsSetUpMixin(TestCase):
    """Mixin com dados reutilizáveis para testes de views de usuário."""

    def setUp(self):
        self.client = Client()

        # Usuário cliente base
        self.client_user = User.objects.create_user(
            username='cliente_teste',
            email='cliente@teste.com',
            password='Senha@Forte123',
            first_name='João',
            last_name='Silva',
            user_type=User.UserType.CLIENT,
        )

        # Usuário vendedor base
        self.seller_user = User.objects.create_user(
            username='vendedor_teste',
            email='vendedor@teste.com',
            password='Senha@Forte123',
            first_name='Maria',
            last_name='Santos',
            user_type=User.UserType.SELLER,
        )

        # URLs
        self.url_register = reverse('users:user-register')
        self.url_login = reverse('users:user-login')
        self.url_logout = reverse('users:user-logout')
        self.url_profile = reverse('users:user-profile')


class TestRegisterView(UserViewsSetUpMixin):
    """Testes para a view de cadastro de novo usuário."""

    def test_register_client_success(self):
        """Cadastro de cliente válido redireciona para home."""
        dados = {
            'email': 'novocliente@teste.com',
            'first_name': 'Pedro',
            'last_name': 'Oliveira',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
            'user_type': User.UserType.CLIENT,
        }
        response = self.client.post(self.url_register, dados)

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertTrue(
            User.objects.filter(email='novocliente@teste.com').exists()
        )

    def test_register_seller_creates_profile(self):
        """Cadastro de vendedor cria automaticamente um SellerProfile via signal."""
        dados = {
            'email': 'novovendedor@teste.com',
            'first_name': 'Ana',
            'last_name': 'Costa',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
            'user_type': User.UserType.SELLER,
        }
        self.client.post(self.url_register, dados)

        user = User.objects.get(email='novovendedor@teste.com')
        self.assertEqual(user.user_type, User.UserType.SELLER)
        self.assertTrue(
            SellerProfile.objects.filter(user=user).exists(),
            'SellerProfile deve ser criado automaticamente para vendedores.',
        )

    def test_register_duplicate_email(self):
        """E-mail já cadastrado deve exibir erro no formulário."""
        dados = {
            'email': 'cliente@teste.com',  # e-mail já existente no setUp
            'first_name': 'Outro',
            'last_name': 'Usuário',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
            'user_type': User.UserType.CLIENT,
        }
        response = self.client.post(self.url_register, dados)

        # Não redireciona — permanece na página com erro
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('email', response.context['form'].errors)

    def test_register_get_renders_form(self):
        """GET na view de cadastro deve renderizar o formulário."""
        response = self.client.get(self.url_register)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIn('form', response.context)

    def test_register_authenticated_user_redirects(self):
        """Usuário já autenticado é redirecionado ao acessar cadastro."""
        self.client.force_login(self.client_user)
        response = self.client.get(self.url_register)

        self.assertRedirects(response, '/', fetch_redirect_response=False)


class TestLoginView(UserViewsSetUpMixin):
    """Testes para a view de login por e-mail."""

    def test_login_by_email_success(self):
        """Login com e-mail e senha corretos redireciona para home."""
        response = self.client.post(self.url_login, {
            'email': 'cliente@teste.com',
            'password': 'Senha@Forte123',
        })

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        # Verifica que sessão foi criada
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_invalid_credentials(self):
        """Credenciais inválidas exibem mensagem de erro e não autenticam."""
        response = self.client.post(self.url_login, {
            'email': 'cliente@teste.com',
            'password': 'SenhaErrada999',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        # Usuário não deve estar autenticado
        self.assertNotIn('_auth_user_id', self.client.session)

        # Verifica mensagem de erro no response
        messages = list(response.context['messages'])
        self.assertTrue(
            any('inválidos' in str(m).lower() or 'inválido' in str(m).lower() for m in messages),
            'Mensagem de erro de credenciais inválidas esperada.',
        )

    def test_login_get_renders_form(self):
        """GET na view de login deve renderizar o formulário."""
        response = self.client.get(self.url_login)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertIn('form', response.context)

    def test_login_authenticated_user_redirects(self):
        """Usuário já autenticado é redirecionado ao acessar login."""
        self.client.force_login(self.client_user)
        response = self.client.get(self.url_login)

        self.assertRedirects(response, '/', fetch_redirect_response=False)


class TestLogoutView(UserViewsSetUpMixin):
    """Testes para a view de logout."""

    def test_logout_redirects(self):
        """Logout (POST) encerra sessão e redireciona para home."""
        self.client.force_login(self.client_user)
        response = self.client.post(self.url_logout)

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_get_not_allowed(self):
        """GET no endpoint de logout deve ser rejeitado (método não permitido)."""
        self.client.force_login(self.client_user)
        response = self.client.get(self.url_logout)

        self.assertEqual(response.status_code, 405)

    def test_logout_requires_login(self):
        """Logout sem autenticação redireciona para login."""
        response = self.client.post(self.url_logout)

        # Redireciona para login (comportamento do @login_required)
        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_logout}',
            fetch_redirect_response=False,
        )


class TestProfileView(UserViewsSetUpMixin):
    """Testes para a view de perfil do usuário."""

    def test_profile_requires_login(self):
        """Acesso ao perfil sem login redireciona para página de login."""
        response = self.client.get(self.url_profile)

        self.assertRedirects(
            response,
            f'/usuarios/login/?next={self.url_profile}',
            fetch_redirect_response=False,
        )

    def test_profile_get_renders_form(self):
        """GET no perfil de cliente autenticado renderiza o formulário."""
        self.client.force_login(self.client_user)
        response = self.client.get(self.url_profile)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertIn('user_form', response.context)

    def test_profile_edit_success(self):
        """Edição de perfil salva os dados e redireciona para o perfil."""
        self.client.force_login(self.client_user)
        response = self.client.post(self.url_profile, {
            'first_name': 'João Editado',
            'last_name': 'Silva Editado',
            'email': 'cliente@teste.com',
        })

        self.assertRedirects(
            response,
            self.url_profile,
            fetch_redirect_response=False,
        )
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.first_name, 'João Editado')
        self.assertEqual(self.client_user.last_name, 'Silva Editado')

    def test_profile_seller_has_seller_form(self):
        """Perfil de vendedor exibe o formulário do SellerProfile."""
        self.client.force_login(self.seller_user)
        response = self.client.get(self.url_profile)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_seller'])
        self.assertIsNotNone(response.context['seller_form'])

    def test_profile_client_has_no_seller_form(self):
        """Perfil de cliente não deve exibir formulário do SellerProfile."""
        self.client.force_login(self.client_user)
        response = self.client.get(self.url_profile)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_seller'])
        self.assertIsNone(response.context['seller_form'])
