"""
Formulários do app users.

LoginForm:
    Formulário simples de login por e-mail e senha.

UserRegistrationForm:
    Formulário de cadastro de novo usuário (cliente ou vendedor).
    Estende UserCreationForm para herdar validação de senhas do Django.
    O campo username não é exposto — é preenchido automaticamente pelo model.

UserProfileForm:
    Edição dos dados básicos do usuário autenticado (nome e e-mail).
    Valida unicidade de e-mail excluindo o próprio usuário.

SellerProfileForm:
    Edição dos dados do SellerProfile (nome da loja, CNPJ, descrição,
    configuração de frete). Disponível apenas para usuários SELLER.

AddressForm:
    Criação e edição de endereço de entrega do usuário.
    Valida formato de CEP (XXXXX-XXX) e UF (2 caracteres maiúsculos).
"""

import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Address, SellerProfile

User = get_user_model()


class LoginForm(forms.Form):
    """Formulário de login por e-mail."""

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "Digite seu e-mail",
            "autocomplete": "email",
        }),
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Digite sua senha",
            "autocomplete": "current-password",
        }),
    )


class UserRegistrationForm(UserCreationForm):
    """
    Formulário de cadastro de novo usuário.

    Campos expostos: email, first_name, last_name, password1, password2, user_type.
    O campo username NÃO é exposto — o model preenche automaticamente via save().

    Validações:
        - E-mail único (case-insensitive)
        - Senhas validadas pelos AUTH_PASSWORD_VALIDATORS do Django
        - Nome e sobrenome obrigatórios
    """

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "seu@email.com",
            "autocomplete": "email",
            "id": "id_email",
        }),
    )

    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Seu nome",
            "autocomplete": "given-name",
            "id": "id_first_name",
        }),
    )

    last_name = forms.CharField(
        label="Sobrenome",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Seu sobrenome",
            "autocomplete": "family-name",
            "id": "id_last_name",
        }),
    )

    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Crie uma senha",
            "autocomplete": "new-password",
            "id": "id_password1",
        }),
    )

    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Repita a senha",
            "autocomplete": "new-password",
            "id": "id_password2",
        }),
    )

    user_type = forms.ChoiceField(
        label="Tipo de conta",
        choices=User.UserType.choices,
        initial=User.UserType.CLIENT,
        widget=forms.RadioSelect(attrs={
            "id": "id_user_type",
        }),
    )

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'user_type',
        )

    def clean_email(self):
        """Valida que o e-mail é único (case-insensitive)."""
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Já existe uma conta com este e-mail.'
            )
        return email


class UserProfileForm(forms.ModelForm):
    """
    Formulário de edição do perfil do usuário autenticado.

    Campos expostos: first_name, last_name, email.
    Valida unicidade de e-mail excluindo o próprio usuário da consulta,
    evitando falso positivo ao resubmeter o mesmo e-mail.
    """

    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Seu nome',
            'autocomplete': 'given-name',
            'id': 'id_profile_first_name',
        }),
    )

    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Seu sobrenome',
            'autocomplete': 'family-name',
            'id': 'id_profile_last_name',
        }),
    )

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
            'id': 'id_profile_email',
        }),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        """Valida unicidade de e-mail excluindo o próprio usuário."""
        email = self.cleaned_data.get('email', '').lower().strip()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email


class SellerProfileForm(forms.ModelForm):
    """
    Formulário de edição do perfil do vendedor.

    Campos: store_name, cnpj, description, shipping_rate_per_km,
    shipping_distance_km.
    Disponível apenas para usuários com user_type = SELLER.
    """

    store_name = forms.CharField(
        label='Nome da loja',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome da sua loja',
            'id': 'id_store_name',
        }),
    )

    cnpj = forms.CharField(
        label='CNPJ',
        max_length=18,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'XX.XXX.XXX/XXXX-XX',
            'id': 'id_cnpj',
        }),
    )

    description = forms.CharField(
        label='Descrição da loja',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Fale sobre sua loja, seus produtos e diferenciais...',
            'rows': 4,
            'id': 'id_description',
        }),
    )

    shipping_rate_per_km = forms.DecimalField(
        label='Valor por km (R$)',
        max_digits=6,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0.00',
            'step': '0.01',
            'id': 'id_shipping_rate_per_km',
        }),
        help_text='Valor em R$ cobrado por quilômetro. Fórmula: frete = distância × valor/km.',
    )

    shipping_distance_km = forms.DecimalField(
        label='Distância de entrega (km)',
        max_digits=8,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0.00',
            'step': '0.01',
            'id': 'id_shipping_distance_km',
        }),
        help_text='Distância estimada em km para cálculo do frete (simulado, sem API de mapas).',
    )

    class Meta:
        model = SellerProfile
        fields = (
            'store_name',
            'cnpj',
            'description',
            'shipping_rate_per_km',
            'shipping_distance_km',
        )


class AddressForm(forms.ModelForm):
    """
    Formulário de criação e edição de endereço de entrega.

    Validações:
        - CEP no formato XXXXX-XXX (8 dígitos com hífen)
        - UF com exatamente 2 letras maiúsculas
    """

    nickname = forms.CharField(
        label='Apelido',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: Casa, Trabalho',
            'id': 'id_addr_nickname',
        }),
    )

    recipient_name = forms.CharField(
        label='Nome do destinatário',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome de quem receberá o pedido',
            'id': 'id_addr_recipient_name',
        }),
    )

    zip_code = forms.CharField(
        label='CEP',
        max_length=9,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'XXXXX-XXX',
            'maxlength': '9',
            'id': 'id_addr_zip_code',
        }),
    )

    street = forms.CharField(
        label='Rua / Logradouro',
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome da rua',
            'id': 'id_addr_street',
        }),
    )

    number = forms.CharField(
        label='Número',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nº',
            'id': 'id_addr_number',
        }),
    )

    complement = forms.CharField(
        label='Complemento',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apto, Bloco, etc.',
            'id': 'id_addr_complement',
        }),
    )

    neighborhood = forms.CharField(
        label='Bairro',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome do bairro',
            'id': 'id_addr_neighborhood',
        }),
    )

    city = forms.CharField(
        label='Cidade',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome da cidade',
            'id': 'id_addr_city',
        }),
    )

    state = forms.CharField(
        label='Estado (UF)',
        max_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'SP',
            'maxlength': '2',
            'id': 'id_addr_state',
        }),
    )

    reference = forms.CharField(
        label='Ponto de referência',
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Próximo ao mercado, portão azul…',
            'id': 'id_addr_reference',
        }),
    )

    is_default = forms.BooleanField(
        label='Definir como endereço padrão',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'id_addr_is_default',
        }),
    )

    class Meta:
        model = Address
        fields = (
            'nickname',
            'recipient_name',
            'zip_code',
            'street',
            'number',
            'complement',
            'neighborhood',
            'city',
            'state',
            'reference',
            'is_default',
        )

    def clean_zip_code(self):
        """Valida o formato do CEP: XXXXX-XXX."""
        zip_code = self.cleaned_data.get('zip_code', '').strip()
        if not re.fullmatch(r'\d{5}-\d{3}', zip_code):
            raise forms.ValidationError(
                'CEP inválido. Use o formato XXXXX-XXX (ex: 01310-100).'
            )
        return zip_code

    def clean_state(self):
        """Valida que a UF tem exatamente 2 letras maiúsculas."""
        state = self.cleaned_data.get('state', '').strip().upper()
        if not re.fullmatch(r'[A-Z]{2}', state):
            raise forms.ValidationError(
                'UF inválida. Use 2 letras maiúsculas (ex: SP, RJ, MG).'
            )
        return state