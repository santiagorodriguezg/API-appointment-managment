"""Users tests"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from tests.users.factory import UserFactory, UserAdminFactory, TokenFactory, UserDoctorFactory
from tests.utils import TEST_PASSWORD


class AccountsAPITestCase(APITestCase):
    """Accounts API test case"""

    def test_signup(self) -> None:
        """Register user with role USER"""

        url = reverse('signup')
        data = {
            "first_name": "Carlos",
            "last_name": "Moreno",
            "identification_type": "CC",
            "identification_number": "10862268",
            "username": "carlos",
            "email": "carlos@gmail.com",
            "phone": "3189523745",
            "city": "",
            "address": "",
            "password": TEST_PASSWORD,
            "password2": TEST_PASSWORD
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, 'Carlos')

    def test_login(self) -> None:
        """Verify user is logged in"""
        user = UserFactory()
        url = reverse('login')
        data = {
            'username': user.username,
            'password': TEST_PASSWORD,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertContains(response, user.role, status_code=status.HTTP_201_CREATED)

    def test_logout(self) -> None:
        """Verify that the user is logged out"""
        url = reverse('logout')
        response = self.client.post(url, {'token': TokenFactory().key})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))


class UsersAPITestCase(APITestCase):
    """Users API test case"""

    def setUp(self) -> None:
        self.user = UserAdminFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_user_admin_list_users(self) -> None:
        """an ADMIN user can list users with all fields"""
        # Users in DB must be 1
        self.assertEqual(User.objects.count(), 1)
        # Create users
        UserDoctorFactory.create_batch(3)

        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 4)

        for i, user in enumerate(User.objects.prefetch_related('groups', 'user_permissions').all()):
            self.assertEqual(response.data[i].get('first_name'), user.first_name)
            self.assertEqual(response.data[i].get('role'), user.role)
            self.assertEqual(response.data[i].get('is_superuser'), user.is_superuser)
            self.assertEqual(response.data[i].get('is_active'), user.is_active)
            self.assertEqual(response.data[i].get('is_staff'), user.is_staff)
            self.assertEqual(response.data[i].get('groups'), list(user.groups.all()))
            self.assertEqual(response.data[i].get('user_permissions'), list(user.user_permissions.all()))

    def test_user_doctor_list_users(self) -> None:
        """Verify that DOCTOR users only see basic user fields."""
        # Authenticate user DOCTOR
        self.user = UserDoctorFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Users in DB must be 2
        self.assertEqual(User.objects.count(), 2)

        # Create users
        UserAdminFactory.create_batch(3)

        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 5)
        for i, user in enumerate(User.objects.prefetch_related('groups', 'user_permissions').all()):
            self.assertEqual(response.data[i].get('first_name'), user.first_name)
            self.assertEqual(response.data[i].get('role'), user.role)
            self.assertIsNone(response.data[i].get('is_superuser'))
            self.assertIsNone(response.data[i].get('is_active'))
            self.assertIsNone(response.data[i].get('is_staff'))
            self.assertIsNone(response.data[i].get('groups'))
            self.assertIsNone(response.data[i].get('user_permissions'))

    def test_user_patient_list_users(self) -> None:
        """Verify that a patient user cannot list users"""
        # Authenticate user PATIENT
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Users in DB must be 2
        self.assertEqual(User.objects.count(), 2)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
