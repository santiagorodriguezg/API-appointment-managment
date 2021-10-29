"""
WSGI config for gestion_consultas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from decouple import config
from django.core.wsgi import get_wsgi_application

settings = 'local' if config('DJANGO_ENV', default='dev') == 'dev' else 'production'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'gestion_consultas.settings.{settings}')

application = get_wsgi_application()
