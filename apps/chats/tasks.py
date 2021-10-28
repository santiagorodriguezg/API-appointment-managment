"""Chats Celery tasks"""

from django.conf import settings
from celery import shared_task

from apps.accounts.models import User
from apps.chats.models import Room
from gestion_consultas.utils import send_email


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_chat_message_notification(user_receiver_pk, user_owner_pk, room_name):
    """
    Sends an e-mail to the user receiving the chat.
    It is used when creating the chat room.
    """
    users = User.objects.filter(pk__in=[user_receiver_pk, user_owner_pk])
    room = Room.objects.get(name=room_name)
    user_receiver = users[0]

    context = {
        'user': user_receiver,
        'user_owner': users[1],
        'chat_url': f'{settings.CLIENT_DOMAIN}/chat/{room.name}'
    }
    send_email(user_receiver.email, 'accounts/email/chat_message_notification', context)
