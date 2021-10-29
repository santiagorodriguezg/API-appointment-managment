"""
ASGI config for gestion_consultas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.urls import re_path
from django.core.asgi import get_asgi_application
from decouple import config

settings = 'local' if config('DJANGO_ENV', default='dev') == 'dev' else 'production'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'gestion_consultas.settings.{settings}')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # NOQA
from channels.routing import ProtocolTypeRouter, URLRouter  # NOQA
from channels.security.websocket import AllowedHostsOriginValidator  # NOQA

from gestion_consultas.middleware import JwtAuthMiddleware  # NOQA
from apps.chats.api.consumers import messages  # NOQA

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JwtAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter([
                    re_path(r'ws/v1/chat/(?P<room_name>\w+)/$', messages.MessageConsumer.as_asgi())
                ])
            )
        )
    )
})
