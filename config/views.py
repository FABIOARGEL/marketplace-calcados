"""
Views centrais do projeto (Landing page / Home).
"""

from django.shortcuts import render


def home(request):
    """
    Página inicial do marketplace.

    Renderiza a landing page com contexto básico (seções de destaque,
    categorias e chamada para ação).
    """
    context = {
        "title": "SoleStep — Calçados para o seu estilo",
    }
    return render(request, "home.html", context)
