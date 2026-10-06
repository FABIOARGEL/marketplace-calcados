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
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import SellerProfile

User = get_user_model()

from .models import Address


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


class AddressForm(forms.ModelForm):
    zip_code = forms.RegexField(
        regex=r"^\d{5}-\d{3}$",
        error_messages={
            "invalid": "Informe o CEP no formato XXXXX-XXX.",
        },
    )

    state = forms.CharField(
        max_length=2,
        min_length=2,
        error_messages={
            "min_length": "A UF deve ter 2 caracteres.",
            "max_length": "A UF deve ter 2 caracteres.",
        },
    )

    class Meta:
        model = Address
        fields = [
            "nickname",
            "recipient_name",
            "zip_code",
            "street",
            "number",
            "complement",
            "neighborhood",
            "city",
            "state",
            "reference",
            "is_default",
        ]

    def clean_state(self):
        state = self.cleaned_data["state"].strip().upper()

        if not state.isalpha():
            raise forms.ValidationError(
                "A UF deve conter apenas letras."
            )

        return state
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
