"""
Testes de gerenciamento de endereços (CRUD e regras de negócio).

Cobre criação, edição, isolamento entre usuários, exclusão e toggle de endereço padrão.
Executável via: python manage.py test tests.users.test_addresses
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.users.models import Address

User = get_user_model()


class AddressTestCase(TestCase):
    """Testes para o CRUD de endereços do app users."""

    def setUp(self):
        self.client = Client()

        # Usuário principal
        self.user = User.objects.create_user(
            username='lucas_mendes',
            email='usuario@teste.com',
            password='Senha@Forte123',
            first_name='Lucas',
            last_name='Mendes',
            user_type=User.UserType.CLIENT,
        )

        # Outro usuário para testar isolamento de dados
        self.other_user = User.objects.create_user(
            username='fernanda_lima',
            email='outro@teste.com',
            password='Senha@Forte123',
            first_name='Fernanda',
            last_name='Lima',
            user_type=User.UserType.CLIENT,
        )

        # Endereço pertencente ao usuário principal
        self.address = Address.objects.create(
            user=self.user,
            nickname='Casa',
            recipient_name='Lucas Mendes',
            zip_code='01310-100',
            street='Avenida Paulista',
            number='1000',
            neighborhood='Bela Vista',
            city='São Paulo',
            state='SP',
            is_default=True,
        )

        # Endereço pertencente ao outro usuário
        self.other_address = Address.objects.create(
            user=self.other_user,
            nickname='Trabalho',
            recipient_name='Fernanda Lima',
            zip_code='20040-001',
            street='Avenida Rio Branco',
            number='500',
            neighborhood='Centro',
            city='Rio de Janeiro',
            state='RJ',
            is_default=True,
        )

        # URLs
        self.url_list = reverse('users:address-list')
        self.url_create = reverse('users:address-create')
        self.url_edit = reverse('users:address-edit', kwargs={'pk': self.address.pk})
        self.url_delete = reverse('users:address-delete', kwargs={'pk': self.address.pk})

    def test_address_create(self):
        """Criação de endereço com sucesso associa ao usuário autenticado."""
        self.client.force_login(self.user)
        dados = {
            'nickname': 'Trabalho',
            'recipient_name': 'Lucas Mendes',
            'zip_code': '04538-133',
            'street': 'Rua Funchal',
            'number': '200',
            'complement': '8º andar',
            'neighborhood': 'Vila Olímpia',
            'city': 'São Paulo',
            'state': 'SP',
            'is_default': False,
        }
        response = self.client.post(self.url_create, dados)

        self.assertRedirects(response, self.url_list, fetch_redirect_response=False)
        self.assertTrue(
            Address.objects.filter(
                user=self.user,
                nickname='Trabalho',
                street='Rua Funchal',
            ).exists()
        )

    def test_address_edit_own(self):
        """Usuário consegue editar com sucesso seu próprio endereço."""
        self.client.force_login(self.user)
        dados = {
            'nickname': 'Casa Nova',
            'recipient_name': 'Lucas Mendes',
            'zip_code': '01310-100',
            'street': 'Avenida Paulista',
            'number': '1050',  # número alterado
            'complement': 'Bloco B',
            'neighborhood': 'Bela Vista',
            'city': 'São Paulo',
            'state': 'SP',
            'is_default': True,
        }
        response = self.client.post(self.url_edit, dados)

        self.assertRedirects(response, self.url_list, fetch_redirect_response=False)
        self.address.refresh_from_db()
        self.assertEqual(self.address.nickname, 'Casa Nova')
        self.assertEqual(self.address.number, '1050')
        self.assertEqual(self.address.complement, 'Bloco B')

    def test_address_cannot_edit_other_user(self):
        """Usuário não pode editar o endereço de outro usuário (retorna 404)."""
        self.client.force_login(self.user)
        url_other_edit = reverse(
            'users:address-edit',
            kwargs={'pk': self.other_address.pk},
        )
        dados = {
            'nickname': 'Hacked',
            'recipient_name': 'Lucas Mendes',
            'zip_code': '20040-001',
            'street': 'Avenida Rio Branco',
            'number': '999',
            'neighborhood': 'Centro',
            'city': 'Rio de Janeiro',
            'state': 'RJ',
        }
        response = self.client.post(url_other_edit, dados)

        self.assertEqual(response.status_code, 404)
        self.other_address.refresh_from_db()
        self.assertNotEqual(self.other_address.nickname, 'Hacked')

    def test_address_delete(self):
        """Usuário consegue excluir seu próprio endereço via POST."""
        self.client.force_login(self.user)
        address_id = self.address.pk

        response = self.client.post(self.url_delete)

        self.assertRedirects(response, self.url_list, fetch_redirect_response=False)
        self.assertFalse(Address.objects.filter(pk=address_id).exists())

    def test_address_cannot_delete_other_user(self):
        """Usuário não pode excluir o endereço de outro usuário (retorna 404)."""
        self.client.force_login(self.user)
        url_other_delete = reverse(
            'users:address-delete',
            kwargs={'pk': self.other_address.pk},
        )
        response = self.client.post(url_other_delete)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Address.objects.filter(pk=self.other_address.pk).exists())

    def test_address_default_toggle(self):
        """Definir um novo endereço como padrão desmarca o padrão anterior."""
        self.client.force_login(self.user)

        # self.address já é padrão (is_default=True)
        self.assertTrue(self.address.is_default)

        # Cria um segundo endereço definindo-o como padrão
        dados_segundo = {
            'nickname': 'Praia',
            'recipient_name': 'Lucas Mendes',
            'zip_code': '11010-000',
            'street': 'Avenida da Praia',
            'number': '42',
            'neighborhood': 'Gonzaga',
            'city': 'Santos',
            'state': 'SP',
            'is_default': True,
        }
        response = self.client.post(self.url_create, dados_segundo)
        self.assertRedirects(response, self.url_list, fetch_redirect_response=False)

        # O primeiro endereço deve ter sido desmarcado como padrão
        self.address.refresh_from_db()
        self.assertFalse(self.address.is_default)

        # O novo endereço deve ser o padrão
        novo_endereco = Address.objects.get(nickname='Praia', user=self.user)
        self.assertTrue(novo_endereco.is_default)

        # E o endereço do outro usuário continua inalterado
        self.other_address.refresh_from_db()
        self.assertTrue(self.other_address.is_default)

    def test_address_list_only_shows_own_addresses(self):
        """A listagem de endereços só exibe os endereços do usuário autenticado."""
        self.client.force_login(self.user)
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, 200)
        enderecos = response.context['addresses']
        self.assertIn(self.address, enderecos)
        self.assertNotIn(self.other_address, enderecos)
