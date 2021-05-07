"""Message consumer tests"""

import json

from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from django.urls import re_path

from apps.chats.api.consumers.messages import MessageConsumer
from tests.accounts.factories import UserAdminFactory, TokenFactory, UserFactory
from tests.chats.factories import MessageFactory, RoomFactory
from tests.utils import API_VERSION_V1


class AuthWebsocketCommunicator(WebsocketCommunicator):
    """Websocket communicator with user scope"""

    def __init__(self, application, path, headers=None, subprotocols=None, user=None):
        super(AuthWebsocketCommunicator, self).__init__(application, path, headers, subprotocols)
        if user is not None:
            self.scope['user'] = user


@database_sync_to_async
def get_user_token(user):
    """Get user token"""
    return TokenFactory(user=user)


@database_sync_to_async
def create_room_and_message(user_owner, user_receiver):
    """Create room and message"""
    room = RoomFactory(user_receiver=user_receiver)
    msg = MessageFactory(room=room, user=user_owner)
    return room, msg


class MessageConsumerTransactionTestCase(TransactionTestCase):
    """Message consumer transaction test case"""

    serialized_rollback = True

    def setUp(self) -> None:
        self.user_owner = UserAdminFactory()
        self.user_receiver = UserFactory()
        self.room_name = 'roomtest'
        self.message = 'Mensaje de prueba'
        self.application = URLRouter([
            re_path(r'ws/v1/chat/(?P<room_name>\w+)/$', MessageConsumer.as_asgi())
        ])

    async def test_create_message_by_user_owner(self) -> None:
        """Create message by a chat room owner user"""
        token = await get_user_token(self.user_owner)
        url = f'/ws/{API_VERSION_V1}/chat/{self.room_name}/?token={token.key}'

        communicator = AuthWebsocketCommunicator(self.application, url, user=self.user_owner)
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.send_json_to({
            'command': 'create_message',
            'data': {
                'room_name': self.room_name,
                'user_receiver': self.user_receiver.id,
                'content': self.message
            }
        })

        response = await communicator.receive_from()
        response = json.loads(response)
        message = response['message']

        self.assertEqual(message['user'], self.user_owner.username)
        self.assertEqual(message['content'], self.message)
        await communicator.disconnect()

    async def test_fetch_messages_by_user_receiver(self) -> None:
        """Get messages by user receiver"""
        room, msg = await create_room_and_message(self.user_owner, self.user_receiver)

        token = await get_user_token(self.user_receiver)
        url = f'/ws/{API_VERSION_V1}/chat/{room.name}/?token={token.key}'

        communicator = AuthWebsocketCommunicator(self.application, url, user=self.user_receiver)
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.send_json_to({
            'command': 'fetch_messages'
        })

        response = await communicator.receive_from()
        response = json.loads(response)
        message = response['messages'][0]

        self.assertEqual(message['id'], msg.id)
        self.assertEqual(message['room'], room.id)
        self.assertEqual(message['user'], self.user_owner.username)
        self.assertEqual(message['content'], msg.content)

        await communicator.disconnect()
