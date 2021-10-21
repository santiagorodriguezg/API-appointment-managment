"""Chats utilities"""

from channels.db import database_sync_to_async

from apps.accounts.models import User
from apps.chats.models import Room, Message


@database_sync_to_async
def create_chat_message(data, user):
    """Create a new message in DB"""
    user_receiver = User.objects.get(username=data['user_receiver'])
    room = Room.objects.filter(name=data['room_name']).first()
    if room is None:
        room = Room.objects.create(
            name=data['room_name'],
            user_owner=user,
            user_receiver=user_receiver
        )

    return Message.objects.create(room=room, user=user, content=data['content'])


@database_sync_to_async
def get_messages(room_name):
    """Get chat room messages"""
    return list(Message.objects.select_related('user').order_by('created_at').filter(room__name=room_name))


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
        'type': message.type,
        'content': message.content,
        'created_at': str(message.created_at),
        'updated_at': str(message.updated_at),
    }
