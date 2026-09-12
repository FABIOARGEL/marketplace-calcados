"""
ASGI config para o Marketplace de Calçados.

Expõe o callable ASGI como variável de módulo: `application`.
Para mais informações, veja:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
