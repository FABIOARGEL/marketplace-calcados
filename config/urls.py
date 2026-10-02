"""
URLs raiz do Marketplace de Calçados.

Rotas principais do projeto.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import include, path


def health_check(request):
    """
    Endpoint simples para verificar se a aplicação está no ar.
    Retorna status 200 com confirmação em JSON.
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Marketplace de Calçados — online'
    })


def home(request):
    return render(request, 'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('', home, name='home'),
    path('', include('apps.users.urls')),
]