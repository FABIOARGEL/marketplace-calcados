"""
URLs do app users.

Prefixo: /usuarios/ (definido em config/urls.py)
"""

from django.urls import path

from .views import profile, register, user_login, user_logout


app_name = "users"

urlpatterns = [
    path("login/", user_login, name="user-login"),
    path("logout/", user_logout, name="user-logout"),
    path("cadastro/", register, name="user-register"),
    path("perfil/", profile, name="user-profile"),
]