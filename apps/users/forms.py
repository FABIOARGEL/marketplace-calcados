from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label="Nome completo",
        max_length=150,
        required=True,
    )

    email = forms.EmailField(
        label="E-mail",
        required=True,
    )

    user_type = forms.ChoiceField(
        label="Tipo de usuário",
        choices=CustomUser.UserType.choices,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            "full_name",
            "email",
            "user_type",
            "password1",
            "password2",
        )

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()

        if len(name.split()) < 2:
            raise forms.ValidationError(
                "Informe seu nome e sobrenome."
            )

        return name

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        full_name = self.cleaned_data["full_name"]
        name_parts = full_name.split()

        user.first_name = name_parts[0]
        user.last_name = " ".join(name_parts[1:])
        user.email = self.cleaned_data["email"]

        # O projeto utiliza username, então o e-mail será usado como login.
        user.username = self.cleaned_data["email"]

        user.user_type = self.cleaned_data["user_type"]

        if commit:
            user.save()

        return user