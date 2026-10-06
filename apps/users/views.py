from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddressForm
from .models import Address


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