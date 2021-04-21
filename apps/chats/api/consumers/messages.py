"""Message consumer"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.chats.utils import create_chat_message, get_messages, message_to_json, messages_to_json


class MessageConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        """
        Constructs all the necessary attributes for the chat room
        """
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.room_name = None
        self.user = None

        self.commands = {
            'fetch_messages': self.fetch_messages,
            'create_message': self.create_message,
        }

    async def connect(self):
        """Connect the chat"""
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_id = f'chat_{self.room_name}'
            await self.channel_layer.group_add(self.room_id, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnect chat
        :param close_code: Chat to disconnect
        """
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive message from WebSocket
        :param text_data: Data from WebSocket
        :param bytes_data: Bytes data
        :return: Command or function to be executed
        """
        data = json.loads(text_data)
        if data['command'] in self.commands:
            method = getattr(self, data['command'])
            await method(data)
        else:
            content = {
                'command': data['command'],
                'messages': "Acción no permitida"
            }
            await self.send(text_data=json.dumps(content))

    async def create_message(self, data):
        """
        Create a new message in the database
        :param data: Client JSON object to create message
        :return: New user message
        """
        message = await create_chat_message(data['data'], self.user)
        content = {
            'command': 'create_message',
            'message': message_to_json(message)
        }

        # Send chat message
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': 'chat_message',
                'message': content,
            }
        )

    async def fetch_messages(self, data):
        """
        Get chat room messages
        :param data: Client JSON object
        :return: All messages in JSON format
        """
        messages = await get_messages(self.room_name)
        content = {
            'command': 'fetch_messages',
            'messages': messages_to_json(messages)
        }
        await self.send(text_data=json.dumps(content))

    async def chat_message(self, event):
        """Receive message from room group and send message to WebSocket"""
        message = event['message']
        await self.send(text_data=json.dumps(message))
