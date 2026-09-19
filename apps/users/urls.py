from django.urls import path

from . import views


app_name = "users"


urlpatterns = [
    path("cadastro/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
]
