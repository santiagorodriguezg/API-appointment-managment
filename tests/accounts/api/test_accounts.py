"""Accounts tests"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from tests.accounts.factories import UserFactory, USER_FACTORY_DICT
from tests.utils import TEST_PASSWORD, RefreshTokenTest


class SignUpAPIViewTest(APITestCase):
    """Register user with role USER"""

    def test_post(self):
        response = self.client.post(reverse('signup'), USER_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, USER_FACTORY_DICT.get('first_name'))


class LoginAPIViewTest(APITestCase):
    """Verify user is logged in"""

    def test_post(self):
        user = UserFactory()
        data = {
            'username': user.username,
            'password': TEST_PASSWORD,
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertContains(response, user.role, status_code=status.HTTP_201_CREATED)


class LogoutAPIViewTest(APITestCase):
    """Verify that the user is logged out"""

    def test_post(self):
        user = UserFactory()
        token = RefreshTokenTest().for_user(user)
        # self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('logout')
        response = self.client.post(url, {'refresh': str(token)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))


class PasswordResetEmailAPIViewTest(APITestCase):

    def test_password_reset_when_user_has_email(self):
        """Reset password when user has email address"""
        user = UserFactory()
        expected = {
            'send_email': True,
            'username': user.username,
            'email': user.email
        }
        response = self.client.post(reverse('password_reset_email'), {'username': user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected)

    def test_password_reset_when_user_has_not_email(self) -> None:
        """Verify reset password when user has no email address"""
        user = UserFactory(email=None)
        expected = {
            'send_email': False,
            'username': user.username,
            'email': user.email
        }
        response = self.client.post(reverse('password_reset_email'), {'username': user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected)
