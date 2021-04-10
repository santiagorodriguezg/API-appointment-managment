"""Auth tests"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.users.utils import generate_token
from tests.users.factory import UserFactory, TokenFactory
from tests.utils import TEST_PASSWORD, USER_DATA


class AccountsAPITestCase(APITestCase):
    """Accounts API test case"""

    def test_signup(self) -> None:
        """Register user with role USER"""
        response = self.client.post(reverse('signup'), USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, USER_DATA.get('first_name'))

    def test_login(self) -> None:
        """Verify user is logged in"""
        user = UserFactory()
        data = {
            'username': user.username,
            'password': TEST_PASSWORD,
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertContains(response, user.role, status_code=status.HTTP_201_CREATED)

    def test_logout(self) -> None:
        """Verify that the user is logged out"""
        url = reverse('logout')
        response = self.client.post(url, {'token': TokenFactory().key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))

    def test_password_reset_when_user_has_email(self) -> None:
        """Reset password when user has email address"""
        user = UserFactory()
        expected = {
            'send_email': True,
            'username': user.username,
            'email': user.email
        }
        response = self.client.post(reverse('password_reset'), {'username': user.username})
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
        response = self.client.post(reverse('password_reset'), {'username': user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected)

    def test_verify_token(self) -> None:
        """Verify JWT token"""
        user = UserFactory()
        token_type = 'password_reset'
        token = generate_token(user, token_type)
        response = self.client.post(reverse('verify_token'), {'token': token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, user.username)
        self.assertContains(response, token_type)
