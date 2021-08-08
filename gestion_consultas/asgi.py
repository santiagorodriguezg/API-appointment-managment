"""
ASGI config for gestion_citas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.urls import re_path
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from decouple import config

from apps.chats.api.consumers import messages
from gestion_consultas.middleware import JwtAuthMiddleware

settings = 'local' if config('DJANGO_ENV', default='dev') == 'dev' else 'production'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'gestion_consultas.settings.{settings}')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
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
