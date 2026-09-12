"""
URLs raiz do Marketplace de Calçados.

Na Sprint 1, apenas o admin e uma rota de health check estão configurados.
As rotas das apps serão adicionadas nas sprints seguintes.
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse


def health_check(request):
    """
    Endpoint simples para verificar se a aplicação está no ar.
    Retorna status 200 com confirmação em JSON.
    """
    return JsonResponse({'status': 'ok', 'message': 'Marketplace de Calçados — online'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
]
