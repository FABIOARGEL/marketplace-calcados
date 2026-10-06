"""
Testes de formulários do app users.

Cobre validações de UserRegistrationForm e AddressForm (CEP, UF e campos obrigatórios).
Executável via: python manage.py test tests.users.test_forms
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.forms import AddressForm, UserRegistrationForm

User = get_user_model()


class TestUserRegistrationForm(TestCase):
    """Testes de validação para o formulário UserRegistrationForm."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='existente_teste',
            email='existente@teste.com',
            password='Senha@Forte123',
            first_name='Existente',
            last_name='Silva',
        )
        self.valid_data = {
            'email': 'novo@teste.com',
            'first_name': 'Carlos',
            'last_name': 'Ferreira',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
            'user_type': User.UserType.CLIENT,
        }

    def test_registration_form_valid(self):
        """Formulário válido com todos os dados preenchidos corretamente."""
        form = UserRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_duplicate_email(self):
        """E-mail duplicado (mesmo case-insensitive) deve invalidar o formulário."""
        data = self.valid_data.copy()
        data['email'] = 'EXISTENTE@teste.com'
        form = UserRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Já existe uma conta com este e-mail.', form.errors['email'])

    def test_registration_form_passwords_mismatch(self):
        """Senhas diferentes devem resultar em erro de validação."""
        data = self.valid_data.copy()
        data['password2'] = 'OutraSenha@123'
        form = UserRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_form_required_fields(self):
        """Campos obrigatórios não preenchidos devem acusar erro."""
        form = UserRegistrationForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('user_type', form.errors)


class TestAddressForm(TestCase):
    """Testes de validação para o formulário AddressForm."""

    def setUp(self):
        self.valid_data = {
            'nickname': 'Casa',
            'recipient_name': 'João Silva',
            'zip_code': '01310-100',
            'street': 'Avenida Paulista',
            'number': '1000',
            'complement': 'Apto 101',
            'neighborhood': 'Bela Vista',
            'city': 'São Paulo',
            'state': 'SP',
            'reference': 'Perto do metrô Trianon-Masp',
            'is_default': False,
        }

    def test_address_form_valid(self):
        """Formulário com dados válidos deve ser validado com sucesso."""
        form = AddressForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_address_form_invalid_cep_format(self):
        """CEP fora do formato XXXXX-XXX deve falhar na validação."""
        ceps_invalidos = [
            '12345678',    # sem hífen
            '1234-567',    # dígitos insuficientes
            '12345-6789',  # dígitos a mais
            'ABCDE-FGH',   # letras
            '01310_100',   # separador incorreto
        ]
        for cep in ceps_invalidos:
            data = self.valid_data.copy()
            data['zip_code'] = cep
            form = AddressForm(data=data)
            self.assertFalse(
                form.is_valid(),
                f'O CEP "{cep}" deveria ser considerado inválido.'
            )
            self.assertIn('zip_code', form.errors)

    def test_address_form_valid_cep(self):
        """CEP no formato correto XXXXX-XXX deve passar na validação."""
        data = self.valid_data.copy()
        data['zip_code'] = '04538-133'
        form = AddressForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['zip_code'], '04538-133')

    def test_address_form_invalid_uf(self):
        """UF fora do formato de 2 letras maiúsculas deve falhar."""
        ufs_invalidas = [
            'SPO',  # 3 letras
            'S',    # 1 letra
            '12',   # números
            'S1',   # alfanumérico
            '',     # vazio
        ]
        for uf in ufs_invalidas:
            data = self.valid_data.copy()
            data['state'] = uf
            form = AddressForm(data=data)
            self.assertFalse(
                form.is_valid(),
                f'A UF "{uf}" deveria ser considerada inválida.'
            )
            self.assertIn('state', form.errors)

    def test_address_form_valid_uf_lowercase_converts(self):
        """UF informada em minúsculas deve ser convertida para maiúsculas e aceita."""
        data = self.valid_data.copy()
        data['state'] = 'sp'
        form = AddressForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['state'], 'SP')

    def test_address_form_required_fields(self):
        """Campos obrigatórios de endereço devem ser exigidos."""
        form = AddressForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('recipient_name', form.errors)
        self.assertIn('zip_code', form.errors)
        self.assertIn('street', form.errors)
        self.assertIn('number', form.errors)
        self.assertIn('neighborhood', form.errors)
        self.assertIn('city', form.errors)
        self.assertIn('state', form.errors)
