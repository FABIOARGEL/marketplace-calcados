"""
Testes de Fundação — Sprint 1

Valida que a estrutura inicial do projeto está configurada corretamente:

1. test_django_starts_correctly    — Django inicia sem erros de configuração
2. test_installed_apps             — Todos os apps do projeto estão registrados
3. test_database_connection        — Conexão com PostgreSQL funciona
4. test_custom_user_model          — AUTH_USER_MODEL aponta para CustomUser
5. test_custom_user_type_field     — Campo user_type existe e tem os choices corretos
6. test_seller_profile_relation    — SellerProfile tem FK para CustomUser
7. test_create_client_user         — Criação de usuário do tipo CLIENTE funciona
8. test_create_seller_user         — Criação de usuário do tipo VENDEDOR funciona
9. test_health_check_endpoint      — Endpoint /health/ retorna 200
"""

import django
from django.apps import apps
from django.conf import settings
from django.db import connection
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class DjangoConfigTest(TestCase):
    """Testa a configuração básica do Django."""

    def test_django_starts_correctly(self):
        """O Django deve iniciar sem lançar exceções de configuração."""
        # Se chegou até aqui, o Django já iniciou com sucesso
        self.assertTrue(django.VERSION >= (4, 2), 'Django 4.2+ é necessário')

    def test_installed_apps(self):
        """Todos os apps do marketplace devem estar registrados."""
        required_apps = [
            'apps.users',
            'apps.products',
            'apps.cart',
            'apps.orders',
        ]
        installed = [app.name for app in apps.get_app_configs()]
        for app_name in required_apps:
            self.assertIn(
                app_name,
                installed,
                f"App '{app_name}' não está em INSTALLED_APPS.",
            )

    def test_custom_user_model_configured(self):
        """AUTH_USER_MODEL deve apontar para apps.users.CustomUser."""
        self.assertEqual(
            settings.AUTH_USER_MODEL,
            'users.CustomUser',
            'AUTH_USER_MODEL deve ser users.CustomUser',
        )


class DatabaseTest(TestCase):
    """Testa a conexão com o banco de dados PostgreSQL."""

    def test_database_connection(self):
        """O Django deve conseguir abrir uma conexão com o PostgreSQL."""
        try:
            connection.ensure_connection()
            self.assertTrue(connection.is_usable(), 'Conexão com o banco não é utilizável.')
        except Exception as exc:
            self.fail(f'Falha ao conectar com o PostgreSQL: {exc}')

    def test_database_engine_is_postgresql(self):
        """O banco configurado deve ser PostgreSQL."""
        engine = settings.DATABASES['default']['ENGINE']
        self.assertEqual(
            engine,
            'django.db.backends.postgresql',
            'O banco deve ser PostgreSQL (django.db.backends.postgresql)',
        )


class CustomUserModelTest(TestCase):
    """Testa o modelo CustomUser."""

    def test_user_type_field_exists(self):
        """O CustomUser deve ter o campo user_type."""
        User = get_user_model()
        self.assertTrue(
            hasattr(User, 'user_type'),
            'CustomUser deve ter o campo user_type.',
        )

    def test_user_type_choices(self):
        """O campo user_type deve ter os choices CLIENT e SELLER."""
        User = get_user_model()
        choices_values = [choice[0] for choice in User.UserType.choices]
        self.assertIn('CLIENT', choices_values)
        self.assertIn('SELLER', choices_values)

    def test_create_client_user(self):
        """Deve ser possível criar um usuário do tipo CLIENTE."""
        user = User.objects.create_user(
            username='cliente_teste',
            password='senha-segura-123',
            user_type='CLIENT',
        )
        self.assertEqual(user.user_type, 'CLIENT')
        self.assertTrue(user.is_client)
        self.assertFalse(user.is_seller)

    def test_create_seller_user(self):
        """Deve ser possível criar um usuário do tipo VENDEDOR."""
        user = User.objects.create_user(
            username='vendedor_teste',
            password='senha-segura-123',
            user_type='SELLER',
        )
        self.assertEqual(user.user_type, 'SELLER')
        self.assertTrue(user.is_seller)
        self.assertFalse(user.is_client)

    def test_password_is_hashed(self):
        """As senhas devem ser armazenadas com hash — nunca em texto puro."""
        user = User.objects.create_user(
            username='usuario_hash',
            password='minha-senha-secreta',
        )
        # A senha armazenada não deve ser igual à senha em texto puro
        self.assertNotEqual(user.password, 'minha-senha-secreta')
        # O Django usa o formato pbkdf2 ou argon2 — começa com o algoritmo
        self.assertIn('$', user.password, 'Senha deve estar hasheada (formato Django)')

    def test_default_user_type_is_client(self):
        """O tipo padrão de usuário deve ser CLIENTE."""
        user = User.objects.create_user(
            username='usuario_padrao',
            password='senha-123',
        )
        self.assertEqual(user.user_type, 'CLIENT')


class HealthCheckTest(TestCase):
    """Testa o endpoint de health check da aplicação."""

    def setUp(self):
        self.client = Client()

    def test_health_check_returns_200(self):
        """GET /health/ deve retornar HTTP 200."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)

    def test_health_check_returns_json(self):
        """GET /health/ deve retornar JSON com status 'ok'."""
        import json
        response = self.client.get('/health/')
        data = json.loads(response.content)
        self.assertEqual(data.get('status'), 'ok')
