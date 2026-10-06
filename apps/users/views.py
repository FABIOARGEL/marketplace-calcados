from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AddressForm, LoginForm
from .models import Address


def user_login(request):
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


@login_required
@require_POST
def user_logout(request):
    logout(request)
    return redirect("home")


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)

    return render(
        request,
        "users/address_list.html",
        {"addresses": addresses},
    )


@login_required
@transaction.atomic
def address_create(request):
    form = AddressForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user

        if address.is_default:
            Address.objects.filter(
                user=request.user,
                is_default=True,
            ).update(is_default=False)

        address.save()

        return redirect("users:address-list")

    return render(
        request,
        "users/address_form.html",
        {
            "form": form,
            "title": "Novo endereço",
        },
    )


@login_required
@transaction.atomic
def address_edit(request, pk):
    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user,
    )

    form = AddressForm(
        request.POST or None,
        instance=address,
    )

    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)

        if address.is_default:
            Address.objects.filter(
                user=request.user,
                is_default=True,
            ).exclude(pk=address.pk).update(is_default=False)

        address.save()

        return redirect("users:address-list")

    return render(
        request,
        "users/address_form.html",
        {
            "form": form,
            "title": "Editar endereço",
            "address": address,
        },
    )


@login_required
def address_delete(request, pk):
    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        address.delete()
        return redirect("users:address-list")

    return render(
        request,
        "users/address_confirm_delete.html",
        {"address": address},
    )