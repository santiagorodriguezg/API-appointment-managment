"""Room tests"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.chats.models import Room, Message
from tests.accounts.factories import UserAdminFactory, UserFactory, UserDoctorFactory
from tests.chats.factories import RoomFactory, MessageFactory
from tests.utils import API_VERSION_V1, AccessTokenTest


class RoomAPITestCase(APITestCase):
    """Room API test case"""

    def setUp(self) -> None:
        self.user_owner = UserAdminFactory()
        self.user_receiver_1 = UserFactory()
        self.user_receiver_2 = UserDoctorFactory()
        self.token = AccessTokenTest().for_user(self.user_owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.token)}')

        self.room_1 = RoomFactory(user_owner=self.user_owner, user_receiver=self.user_receiver_1)
        self.room_2 = RoomFactory(user_owner=self.user_owner, user_receiver=self.user_receiver_2)

        MessageFactory(room=self.room_1, user=self.user_owner)
        MessageFactory(room=self.room_1, user=self.user_receiver_1)
        MessageFactory(room=self.room_1, user=self.user_owner)

        MessageFactory(room=self.room_2, user=self.user_owner)
        MessageFactory.create_batch(2, room=self.room_2, user=self.user_receiver_2)
        MessageFactory(room=self.room_2, user=self.user_owner)

    def test_list_chat_rooms_by_owner(self) -> None:
        """List of chat rooms where the user is an owner"""
        url = f'/{API_VERSION_V1}/users/{self.user_owner.username}/rooms/'
        response = self.client.get(url)
        rooms = response.data['results']['rooms']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = Room.objects.select_related('user_receiver').filter(user_owner=self.user_owner)
        for i, room in enumerate(queryset):
            self.assertEqual(rooms[i]['id'], room.id)
            self.assertEqual(rooms[i]['name'], room.name)
            self.assertEqual(rooms[i]['user_receiver']['username'], room.user_receiver.username)

        # Listar salas de chat asociadas a otro usuario
        url = f'/{API_VERSION_V1}/users/{self.user_receiver_1.username}/rooms/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_chat_rooms_by_receiver(self):
        """List of chat rooms in which the user is a receiver"""
        token = AccessTokenTest().for_user(self.user_receiver_1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')

        url = f'/{API_VERSION_V1}/users/{self.user_receiver_1.username}/rooms/'
        response = self.client.get(url)
        rooms = response.data['results']['rooms']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

        queryset = Room.objects.select_related('user_owner').filter(user_receiver=self.user_receiver_1)
        for i, room in enumerate(queryset):
            self.assertEqual(rooms[i]['id'], room.id)
            self.assertEqual(rooms[i]['name'], room.name)
            self.assertEqual(rooms[i]['user_owner']['username'], room.user_owner.username)

        # Listar salas de chat asociadas a otro usuario
        url = f'/{API_VERSION_V1}/users/{self.user_receiver_2.username}/rooms/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_chat_rooms_by_owner(self):
        """Chat room given an Id in which the user is a owner"""
        url = f'/{API_VERSION_V1}/users/{self.user_owner.username}/rooms/{self.room_1.id}/'
        response = self.client.get(url)
        room = response.data['room']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(room['id'], self.room_1.id)
        self.assertEqual(room['name'], self.room_1.name)
        self.assertEqual(room['user_receiver']['username'], self.room_1.user_receiver.username)

        # Obtener sala de chat asociadas a otro usuario
        url = f'/{API_VERSION_V1}/users/{self.user_receiver_1.username}/rooms/{self.room_1.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_chat_rooms_by_receiver(self):
        """Chat room given an Id in which the user is a receiver"""
        token = AccessTokenTest().for_user(self.user_receiver_2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')

        url = f'/{API_VERSION_V1}/users/{self.user_receiver_2.username}/rooms/{self.room_2.id}/'
        response = self.client.get(url)
        room = response.data['room']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(room['id'], self.room_2.id)
        self.assertEqual(room['name'], self.room_2.name)
        self.assertEqual(room['user_owner']['username'], self.room_2.user_owner.username)

        # Obtener sala de chat asociadas a otro usuario
        url = f'/{API_VERSION_V1}/users/{self.user_owner.username}/rooms/{self.room_1.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_chat_rooms_with_messages_by_owner(self):
        """Chat room with messages given an Id in which the user is a owner"""
        url = f'/{API_VERSION_V1}/users/{self.user_owner.username}/rooms/{self.room_1.id}/messages/'
        response = self.client.get(url)
        room = response.data['room']
        messages = room['messages']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(room['id'], self.room_1.id)

        queryset = Message.objects.select_related('user').order_by('created_at').filter(room__name=self.room_1.name)
        for i, msg in enumerate(queryset):
            self.assertEqual(messages[i]['id'], msg.id)
            self.assertEqual(messages[i]['user'], msg.user.username)

        # Obtener sala de chat asociadas a otro usuario
        url = f'/{API_VERSION_V1}/users/{self.user_receiver_1.username}/rooms/{self.room_1.id}/messages/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_chat_rooms_with_messages_by_receiver(self):
        """Chat room with messages given an Id in which the user is a receiver"""
        token = AccessTokenTest().for_user(self.user_receiver_2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')
        url = f'/{API_VERSION_V1}/users/{self.user_receiver_2.username}/rooms/{self.room_2.id}/messages/'

        response = self.client.get(url)
        room = response.data['room']
        messages = room['messages']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(room['id'], self.room_2.id)

        queryset = Message.objects.select_related('user').order_by('created_at').filter(room__name=self.room_2.name)
        for i, msg in enumerate(queryset):
            self.assertEqual(messages[i]['id'], msg.id)
            self.assertEqual(messages[i]['user'], msg.user.username)

        # Obtener sala de chat asociadas a otro usuario
        url = f'/{API_VERSION_V1}/users/{self.user_owner.username}/rooms/{self.room_1.id}/messages/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
