"""
ASGI config for gestion_citas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

from gestion_consultas.middleware import TokenAuthMiddleware
from apps.chats.api.consumers import messages

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings.local')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/chat/(?P<room_name>\w+)/$', messages.MessageConsumer.as_asgi())
        ])
    ),
    # 'websocket': AllowedHostsOriginValidator(
    #     TokenAuthMiddleware(
    #         URLRouter([
    #             re_path(r'ws/chat/(?P<room_name>\w+)/$', messages.MessageConsumer())
    #         ])
    #     )
    # )
})
