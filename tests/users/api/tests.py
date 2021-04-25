"""Users tests"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from tests.users.factories import (
    UserFactory, UserAdminFactory, TokenFactory, UserDoctorFactory, USER_FACTORY_DICT, USER_ADMIN_FACTORY_DICT,
    USER_DOCTOR_FACTORY_DICT
)
from tests.utils import TEST_PASSWORD, API_VERSION_V1


class UsersAdminAPITestCase(APITestCase):
    """Users with ADMIN role API test case"""

    def setUp(self) -> None:
        # Authenticate user ADMIN
        self.user = UserAdminFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/{API_VERSION_V1}/users/'

    def test_user_admin_create_users(self) -> None:
        """Verify that an ADMIN user can create users"""
        response = self.client.post(self.url, USER_ADMIN_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data.get('first_name'), USER_ADMIN_FACTORY_DICT.get('first_name'))

    def test_user_admin_list_users(self) -> None:
        """An ADMIN user can list users with all fields"""
        # Users in DB must be 1
        self.assertEqual(User.objects.count(), 1)
        # Create users
        UserDoctorFactory.create_batch(3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 4)

        res = response.data.get('results')
        for i, user in enumerate(User.objects.prefetch_related('groups', 'user_permissions').all()[:2]):
            self.assertEqual(res[i].get('first_name'), user.first_name)
            self.assertEqual(res[i].get('role'), user.role)
            self.assertEqual(res[i].get('is_superuser'), user.is_superuser)
            self.assertEqual(res[i].get('is_active'), user.is_active)
            self.assertEqual(res[i].get('is_staff'), user.is_staff)
            self.assertEqual(res[i].get('groups'), list(user.groups.values_list('id', flat=True)))
            self.assertEqual(res[i].get('user_permissions'), list(user.user_permissions.all()))

    def test_user_admin_retrieve_user(self) -> None:
        """An ADMIN user can retrieve one user"""
        users = UserDoctorFactory.create_batch(3)
        response = self.client.get(f'{self.url}{users[1].username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(users[1].first_name, response.data.get('first_name'))

    def test_user_admin_update_user(self) -> None:
        """Update users for given username"""
        users = UserDoctorFactory.create_batch(3)
        response = self.client.put(f'{self.url}{users[1].username}/', USER_ADMIN_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.data.get('first_name'), USER_ADMIN_FACTORY_DICT.get('first_name'))

    def test_user_admin_password_reset(self) -> None:
        """Verify that ADMIN user can send a password reset link"""
        user = UserFactory(email=None)
        url = f'{self.url}{user.username}/password-reset/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertContains(response, 'password_reset_url')


class UsersDoctorAPITestCase(APITestCase):
    """Users with DOCTOR role API test case"""

    def setUp(self) -> None:
        # Authenticate user DOCTOR
        self.user = UserDoctorFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/{API_VERSION_V1}/users/'

    def test_user_doctor_create_users(self) -> None:
        """Verify that an DOCTOR user can not create users"""
        response = self.client.post(self.url, USER_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 1)

    def test_user_doctor_list_users(self) -> None:
        """Verify that DOCTOR users only see basic user fields."""
        # Users in DB must be 1
        self.assertEqual(User.objects.count(), 1)

        # Create users
        UserFactory.create_batch(4)

        response = self.client.get(f'{self.url}?limit=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 5)

        res = response.data.get('results')
        for i, user in enumerate(User.objects.order_by('id')[:3]):
            self.assertEqual(res[i].get('first_name'), user.first_name)
            self.assertEqual(res[i].get('role'), user.role)
            self.assertIsNone(res[i].get('is_superuser'))
            self.assertIsNone(res[i].get('is_active'))
            self.assertIsNone(res[i].get('is_staff'))
            self.assertIsNone(res[i].get('groups'))
            self.assertIsNone(res[i].get('user_permissions'))

    def test_user_doctor_retrieve_user(self) -> None:
        """Verify that DOCTOR users only see basic user fields for one user."""
        users = UserFactory.create_batch(3)
        response = self.client.get(f'{self.url}{users[1].username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(users[1].last_name, response.data.get('last_name'))

    def test_user_doctor_update_user(self) -> None:
        """Verify that a DOCTOR user cannot update users for given username"""
        users = UserDoctorFactory.create_batch(3)
        response = self.client.put(f'{self.url}{users[1].username}/', USER_ADMIN_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 4)

    def test_user_doctor_password_reset(self) -> None:
        """Verify that DOCTOR user can not send a password reset link"""
        user = UserFactory(email=None)
        url = f'{self.url}{user.username}/password-reset/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UsersPatientAPITestCase(APITestCase):
    """Users with PATIENT role API test case"""

    def setUp(self) -> None:
        # Authenticate user PATIENT
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/{API_VERSION_V1}/users/'

    def test_user_patient_create_users(self):
        """Verify that an patient user can not create users"""
        response = self.client.post(self.url, USER_ADMIN_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 1)

    def test_user_patient_list_users(self) -> None:
        """Verify that a patient user cannot list users"""
        self.assertEqual(User.objects.count(), 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_patient_retrieve_user(self) -> None:
        """Verify that patient users can not retrieve users"""
        users = UserFactory.create_batch(3)
        response = self.client.get(f'{self.url}{users[1].id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_patient_update_user(self) -> None:
        """Verify that a patient user cannot update users for given username"""
        users = UserDoctorFactory.create_batch(3)
        response = self.client.put(f'{self.url}{users[1].username}/', USER_DOCTOR_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 4)

    def test_user_patient_password_reset(self) -> None:
        """Verify that patient user can not send a password reset link"""
        user = UserFactory(email=None)
        url = f'{self.url}{user.username}/password-reset/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UsersAPITestCase(APITestCase):
    """Users API test case"""

    def setUp(self) -> None:
        # Authenticate user PATIENT
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/{API_VERSION_V1}/users/'

    def test_my_profile(self) -> None:
        """Obtain the profile of the logged in user"""
        response = self.client.get(f'{self.url}me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), self.user.first_name, )

    def test_update_profile(self) -> None:
        """Verify that the user can update his profile"""
        response = self.client.put(f'{self.url}me/', USER_FACTORY_DICT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('first_name'), USER_FACTORY_DICT.get('first_name'))

    def test_change_password(self) -> None:
        """Verify that the user can change his password"""
        pwd = 'lg654321'
        data = {
            "password_old": TEST_PASSWORD,
            "password": pwd,
            "password2": pwd
        }
        response = self.client.post(f'{self.url}change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))

        # Verify user login
        data = {
            'username': self.user.username,
            'password': pwd,
        }
        response = self.client.post(reverse('accounts-login'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertContains(response, self.user.role, status_code=status.HTTP_201_CREATED)
