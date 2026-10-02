from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Cadastro realizado com sucesso! Agora você pode entrar.",
            )

            return redirect("users:login")
    else:
        form = RegisterForm()

    return render(
        request,
        "users/register.html",
        {"form": form},
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("/")

        messages.error(
            request,
            "E-mail/usuário ou senha inválidos.",
        )

    return render(request, "users/login.html")