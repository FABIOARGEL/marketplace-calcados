
from django import forms


class LoginForm(forms.Form):
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