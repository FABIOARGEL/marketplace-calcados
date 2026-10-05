"""
Formulários do app users.

LoginForm:
    Formulário simples de login por e-mail e senha.

UserRegistrationForm:
    Formulário de cadastro de novo usuário (cliente ou vendedor).
    Estende UserCreationForm para herdar validação de senhas do Django.
    O campo username não é exposto — é preenchido automaticamente pelo model.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

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