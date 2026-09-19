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
10. test_login_by_email            — Autenticação funciona por e-mail (não username)
11. test_email_is_unique           — E-mail deve ser único por usuário
12. test_address_model             — Modelo Address existe e pode ser criado
13. test_seller_shipping_fields    — SellerProfile possui campos de frete
14. test_order_payment_fields      — Order possui campos de pagamento simulado
15. test_order_address_field       — Order possui FK para Address
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

    def test_authentication_backend_configured(self):
        """EmailBackend deve estar configurado como backend de autenticação."""
        backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        self.assertIn(
            'apps.users.backends.EmailBackend',
            backends,
            'EmailBackend deve estar em AUTHENTICATION_BACKENDS.',
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
        self.assertTrue(
            hasattr(User, 'user_type'),
            'CustomUser deve ter o campo user_type.',
        )

    def test_user_type_choices(self):
        """O campo user_type deve ter os choices CLIENT e SELLER."""
        choices_values = [choice[0] for choice in User.UserType.choices]
        self.assertIn('CLIENT', choices_values)
        self.assertIn('SELLER', choices_values)

    def test_username_field_is_email(self):
        """O campo de login (USERNAME_FIELD) deve ser 'email'."""
        self.assertEqual(
            User.USERNAME_FIELD,
            'email',
            'USERNAME_FIELD do CustomUser deve ser email (login por e-mail).',
        )

    def test_create_client_user(self):
        """Deve ser possível criar um usuário do tipo CLIENTE."""
        user = User.objects.create_user(
            username='cliente_teste',
            email='cliente@teste.com',
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
            email='vendedor@teste.com',
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
            email='hash@teste.com',
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
            email='padrao@teste.com',
            password='senha-123',
        )
        self.assertEqual(user.user_type, 'CLIENT')

    def test_email_must_be_unique(self):
        """Dois usuários não podem ter o mesmo e-mail."""
        from django.db import IntegrityError
        User.objects.create_user(
            username='user1',
            email='duplicado@teste.com',
            password='senha-123',
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='duplicado@teste.com',
                password='senha-456',
            )

    def test_login_by_email(self):
        """A autenticação deve funcionar usando e-mail como identificador."""
        from django.contrib.auth import authenticate
        User.objects.create_user(
            username='emailuser',
            email='login@teste.com',
            password='senha-segura-abc',
        )
        # Testa autenticação via e-mail
        authenticated_user = authenticate(
            username='login@teste.com',
            password='senha-segura-abc',
        )
        self.assertIsNotNone(
            authenticated_user,
            'Autenticação por e-mail deve funcionar.',
        )

    def test_login_by_wrong_email_fails(self):
        """Autenticação com e-mail errado deve falhar."""
        from django.contrib.auth import authenticate
        User.objects.create_user(
            username='emailuser2',
            email='correto@teste.com',
            password='senha-segura-xyz',
        )
        result = authenticate(
            username='errado@teste.com',
            password='senha-segura-xyz',
        )
        self.assertIsNone(result, 'E-mail incorreto não deve autenticar.')


class AddressModelTest(TestCase):
    """Testa o modelo Address."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario_end',
            email='endereco@teste.com',
            password='senha-123',
        )

    def test_address_model_exists(self):
        """O modelo Address deve existir no app users."""
        from apps.users.models import Address
        self.assertTrue(hasattr(Address, 'user'), 'Address deve ter FK para usuário.')
        self.assertTrue(hasattr(Address, 'zip_code'), 'Address deve ter campo zip_code.')
        self.assertTrue(hasattr(Address, 'city'), 'Address deve ter campo city.')

    def test_create_address(self):
        """Deve ser possível criar um endereço para um usuário."""
        from apps.users.models import Address
        address = Address.objects.create(
            user=self.user,
            recipient_name='João Silva',
            zip_code='01310-100',
            street='Av. Paulista',
            number='1000',
            neighborhood='Bela Vista',
            city='São Paulo',
            state='SP',
        )
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.city, 'São Paulo')

    def test_user_can_have_multiple_addresses(self):
        """Um usuário deve poder ter vários endereços cadastrados."""
        from apps.users.models import Address
        Address.objects.create(
            user=self.user,
            recipient_name='João Silva',
            zip_code='01310-100',
            street='Av. Paulista',
            number='1000',
            neighborhood='Bela Vista',
            city='São Paulo',
            state='SP',
            nickname='Trabalho',
        )
        Address.objects.create(
            user=self.user,
            recipient_name='João Silva',
            zip_code='04038-001',
            street='Rua das Flores',
            number='25',
            neighborhood='Vila Mariana',
            city='São Paulo',
            state='SP',
            nickname='Casa',
        )
        self.assertEqual(self.user.addresses.count(), 2)


class SellerShippingFieldsTest(TestCase):
    """Testa os campos de frete no SellerProfile."""

    def test_seller_profile_has_shipping_fields(self):
        """SellerProfile deve ter os campos shipping_rate_per_km e shipping_distance_km."""
        from apps.users.models import SellerProfile
        self.assertTrue(
            hasattr(SellerProfile, 'shipping_rate_per_km'),
            'SellerProfile deve ter shipping_rate_per_km.',
        )
        self.assertTrue(
            hasattr(SellerProfile, 'shipping_distance_km'),
            'SellerProfile deve ter shipping_distance_km.',
        )

    def test_shipping_calculation(self):
        """Deve calcular frete = distância × taxa/km corretamente."""
        from decimal import Decimal
        from apps.users.models import SellerProfile
        seller_user = User.objects.create_user(
            username='vendedor_frete',
            email='frete@loja.com',
            password='senha-123',
            user_type='SELLER',
        )
        profile = SellerProfile.objects.create(
            user=seller_user,
            store_name='Loja Teste',
            shipping_rate_per_km=Decimal('2.50'),
            shipping_distance_km=Decimal('30.00'),
        )
        expected_shipping = Decimal('75.00')  # 30 × 2.50
        self.assertEqual(profile.calculate_shipping(), expected_shipping)


class OrderPaymentFieldsTest(TestCase):
    """Testa os campos de pagamento simulado e endereço no modelo Order."""

    def setUp(self):
        from apps.users.models import Address
        from apps.orders.models import Order
        self.user = User.objects.create_user(
            username='pedido_user',
            email='pedido@teste.com',
            password='senha-123',
        )
        self.address = Address.objects.create(
            user=self.user,
            recipient_name='Maria Costa',
            zip_code='20040-020',
            street='Av. Rio Branco',
            number='500',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
        )

    def test_order_has_payment_fields(self):
        """Order deve ter os campos de pagamento simulado."""
        from apps.orders.models import Order
        self.assertTrue(hasattr(Order, 'payment_method'))
        self.assertTrue(hasattr(Order, 'payment_status'))

    def test_order_has_shipping_fields(self):
        """Order deve ter os campos de frete."""
        from apps.orders.models import Order
        self.assertTrue(hasattr(Order, 'shipping_cost'))
        self.assertTrue(hasattr(Order, 'subtotal'))

    def test_order_has_address_fk(self):
        """Order deve ter FK para Address."""
        from apps.orders.models import Order
        self.assertTrue(hasattr(Order, 'shipping_address'))

    def test_create_order_with_simulated_payment(self):
        """Deve ser possível criar um pedido com pagamento simulado."""
        from decimal import Decimal
        from apps.orders.models import Order
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            subtotal=Decimal('299.90'),
            shipping_cost=Decimal('75.00'),
            total=Decimal('374.90'),
            payment_method='PIX_SIM',
            payment_status='APPROVED',
        )
        self.assertEqual(order.payment_method, 'PIX_SIM')
        self.assertEqual(order.payment_status, 'APPROVED')
        self.assertEqual(order.shipping_address, self.address)


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
