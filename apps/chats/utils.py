"""Chats utilities"""

import pytz
from django.utils import timezone
from channels.db import database_sync_to_async

from apps.accounts.models import User
from apps.chats.models import Room, Message


def convert_to_localtime(utctime):
    """
    Converts UTC date to local date.
    :param utctime: UTC date
    :return: Date converted into 12-hour format
    """
    fmt = '%d/%m/%Y %I:%M %p'
    utc = utctime.replace(tzinfo=pytz.UTC)
    local_tz = utc.astimezone(timezone.get_current_timezone())
    return local_tz.strftime(fmt)


@database_sync_to_async
def create_chat_message(data, user):
    """Create a new message in DB"""
    user_receiver = User.objects.get(pk=data['user_receiver'])
    room = Room.objects.filter(name=data['room_name']).first()
    if room is None:
        room = Room.objects.create(
            name=data['room_name'],
            user_owner=user,
            user_receiver=user_receiver
        )

    message = Message.objects.create(room=room, user=user, content=data['content'])
    return message


@database_sync_to_async
def get_messages(room_name):
    """Get chat room messages"""
    return list(Message.objects.select_related('user').filter(room__name=room_name))


def messages_to_json(messages):
    """
    Converts all message objects in the list to JSON format
    :param messages: Message object list
    :return: All messages in JSON format
    """
    result = []
    for message in messages:
        result.append(message_to_json(message))
    return result


def message_to_json(message):
    """
    Converts a message object to JSON format
    :param message: Message object
    :return: Message in JSON format
    """
    return {
        'id': message.id,
        'room': message.room_id,
        'user': message.user.username,
        'content': message.content,
        'created_at': convert_to_localtime(message.created_at),
        'updated_at': convert_to_localtime(message.updated_at),
    }
