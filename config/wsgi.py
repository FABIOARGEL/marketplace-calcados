"""
WSGI config para o Marketplace de Calçados.

Expõe o callable WSGI como variável de módulo: `application`.
Para mais informações, veja:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
