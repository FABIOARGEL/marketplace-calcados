"""
Views do app users.

user_login: Autenticação por e-mail e senha.
user_logout: Encerramento de sessão (POST only).
register: Cadastro de novo usuário (cliente ou vendedor).
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, UserRegistrationForm


def user_login(request):
    """
    View de login por e-mail.

    GET: exibe formulário de login.
    POST: autentica usuário e redireciona para home ou next.
    """
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:
            login(request, user)

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect(settings.LOGIN_REDIRECT_URL)

        messages.error(request, "E-mail ou senha inválidos.")

    return render(
        request,
        "users/login.html",
        {"form": form},
    )


def register(request):
    """
    View de cadastro de novo usuário.

    GET: exibe formulário de cadastro.
    POST: valida dados, cria usuário (CLIENT ou SELLER),
          faz login automático e redireciona para home.

    O SellerProfile é criado automaticamente via signal post_save
    quando user_type = SELLER (ver apps/users/signals.py).
    """
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Login automático após cadastro
            login(
                request,
                user,
                backend='apps.users.backends.EmailBackend',
            )
            messages.success(
                request,
                f'Bem-vindo(a), {user.first_name}! '
                'Sua conta foi criada com sucesso.'
            )
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = UserRegistrationForm()

    return render(
        request,
        'users/register.html',
        {'form': form},
    )


@login_required
@require_POST
def user_logout(request):
    """Encerra a sessão do usuário (somente POST)."""
    logout(request)
    return redirect("home")