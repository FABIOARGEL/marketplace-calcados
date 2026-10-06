from django import forms

from .models import Address


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