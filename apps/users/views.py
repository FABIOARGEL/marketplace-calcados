"""
Views do app users.

user_login: Autenticação por e-mail e senha.
user_logout: Encerramento de sessão (POST only).
register: Cadastro de novo usuário (cliente ou vendedor).
profile: Exibição e edição dos dados cadastrais do usuário logado.
         Vendedores também editam dados do SellerProfile (frete incluso).
address_list: Lista endereços do usuário logado.
address_create: Formulário + criação de novo endereço.
address_edit: Edição de endereço existente (somente do próprio usuário).
address_delete: Exclusão de endereço (somente do próprio usuário).
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AddressForm, LoginForm, SellerProfileForm, UserProfileForm, UserRegistrationForm
from .models import Address


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


def home(request):
    return render(request, "home.html")


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


@login_required
def profile(request):
    """
    View de exibição e edição do perfil do usuário autenticado.

    GET: exibe dados do usuário e, se vendedor, dados do SellerProfile.
    POST: valida e salva as alterações. Vendedores têm dois formulários
          submetidos no mesmo POST (user_form e seller_form).

    Mensagens:
        success — dados salvos com sucesso.
        error   — há erros de validação nos formulários.
    """
    user = request.user
    is_seller = user.is_seller
    seller_profile = getattr(user, 'seller_profile', None)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        seller_form = (
            SellerProfileForm(request.POST, instance=seller_profile)
            if is_seller
            else None
        )

        user_form_valid = user_form.is_valid()
        seller_form_valid = (seller_form.is_valid() if seller_form else True)

        if user_form_valid and seller_form_valid:
            user_form.save()
            if seller_form:
                seller_form.save()
            messages.success(
                request,
                'Seus dados foram atualizados com sucesso!'
            )
            return redirect('users:user-profile')

        messages.error(
            request,
            'Corrija os erros abaixo antes de salvar.'
        )
    else:
        user_form = UserProfileForm(instance=user)
        seller_form = (
            SellerProfileForm(instance=seller_profile)
            if is_seller
            else None
        )

    return render(
        request,
        'users/profile.html',
        {
            'user_form': user_form,
            'seller_form': seller_form,
            'is_seller': is_seller,
        },
    )


# ---------------------------------------------------------------------------
# Endereços de entrega
# ---------------------------------------------------------------------------

@login_required
def address_list(request):
    """
    Lista todos os endereços de entrega do usuário autenticado.

    Endereços são exibidos com o padrão em primeiro lugar
    (ordem definida pelo model: -is_default, -created_at).
    """
    addresses = request.user.addresses.all()
    return render(
        request,
        'users/address_list.html',
        {'addresses': addresses},
    )


@login_required
@transaction.atomic
def address_create(request):
    """
    Cria um novo endereço de entrega para o usuário autenticado.

    GET: exibe formulário vazio.
    POST: valida e salva o endereço.
          Se is_default=True, desmarca todos os outros endereços do usuário.
    """
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default:
                request.user.addresses.filter(is_default=True).update(is_default=False)

            address.save()
            messages.success(request, 'Endereço adicionado com sucesso!')
            return redirect('users:address-list')
    else:
        form = AddressForm()

    return render(
        request,
        'users/address_form.html',
        {'form': form, 'action': 'Novo endereço'},
    )


@login_required
@transaction.atomic
def address_edit(request, pk):
    """
    Edita um endereço de entrega existente.

    Somente o proprietário do endereço pode editá-lo.
    Se is_default=True, desmarca todos os outros endereços do usuário.

    GET: exibe formulário preenchido.
    POST: valida e salva as alterações.
    """
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            addr = form.save(commit=False)

            if addr.is_default:
                request.user.addresses.exclude(pk=pk).filter(is_default=True).update(is_default=False)

            addr.save()
            messages.success(request, 'Endereço atualizado com sucesso!')
            return redirect('users:address-list')
    else:
        form = AddressForm(instance=address)

    return render(
        request,
        'users/address_form.html',
        {'form': form, 'action': 'Editar endereço', 'address': address},
    )


@login_required
def address_delete(request, pk):
    """
    Exclui um endereço de entrega.

    Somente o proprietário do endereço pode excluí-lo.
    GET: exibe página de confirmação de exclusão.
    POST: realiza a exclusão e redireciona para a lista.
    """
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Endereço removido com sucesso!')
        return redirect('users:address-list')

    return render(
        request,
        'users/address_confirm_delete.html',
        {'address': address},
    )