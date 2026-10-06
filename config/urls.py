"""
URLs raiz do Marketplace de Calçados.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.users.views import home


def health_check(request):
    """Verifica se a aplicação está no ar."""
    return JsonResponse({
        "status": "ok",
        "message": "Marketplace de Calçados — online",
    })


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("usuarios/", include("apps.users.urls")),
]