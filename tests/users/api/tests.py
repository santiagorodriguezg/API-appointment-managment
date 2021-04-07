"""Users tests"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from tests.users.factory import UserFactory, UserAdminFactory, TokenFactory, UserDoctorFactory
from tests.utils import TEST_PASSWORD, USER_DATA


class AccountsAPITestCase(APITestCase):
    """Accounts API test case"""

    def test_signup(self) -> None:
        """Register user with role USER"""

        USER_DATA.setdefault('password', TEST_PASSWORD)
        USER_DATA.setdefault('password2', TEST_PASSWORD)
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


class UsersAdminAPITestCase(APITestCase):
    """Users with ADMIN role API test case"""

    def setUp(self) -> None:
        # Authenticate user ADMIN
        self.user = UserAdminFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/users/'

    def test_user_admin_create_users(self) -> None:
        """Verify that an ADMIN user can create users"""
        response = self.client.post(self.url, USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data.get('first_name'), USER_DATA.get('first_name'))

    def test_user_admin_list_users(self) -> None:
        """An ADMIN user can list users with all fields"""
        # Users in DB must be 1
        self.assertEqual(User.objects.count(), 1)
        # Create users
        UserDoctorFactory.create_batch(3)

        response = self.client.get(self.url)
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

    def test_user_admin_retrieve_user(self) -> None:
        """An ADMIN user can retrieve one user"""
        # Create users
        users = UserDoctorFactory.create_batch(3)
        response = self.client.get(f'{self.url}{users[1].id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(users[1].first_name, response.data.get('first_name'))


class UsersDoctorAPITestCase(APITestCase):
    """Users with DOCTOR role API test case"""

    def setUp(self) -> None:
        # Authenticate user DOCTOR
        self.user = UserDoctorFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/users/'

    def test_user_doctor_create_users(self) -> None:
        """Verify that an DOCTOR user can not create users"""
        response = self.client.post(self.url, USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 1)

    def test_user_doctor_list_users(self) -> None:
        """Verify that DOCTOR users only see basic user fields."""
        # Users in DB must be 1
        self.assertEqual(User.objects.count(), 1)

        # Create users
        UserAdminFactory.create_batch(3)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 4)
        for i, user in enumerate(User.objects.prefetch_related('groups', 'user_permissions').all()):
            self.assertEqual(response.data[i].get('first_name'), user.first_name)
            self.assertEqual(response.data[i].get('role'), user.role)
            self.assertIsNone(response.data[i].get('is_superuser'))
            self.assertIsNone(response.data[i].get('is_active'))
            self.assertIsNone(response.data[i].get('is_staff'))
            self.assertIsNone(response.data[i].get('groups'))
            self.assertIsNone(response.data[i].get('user_permissions'))

    def test_user_doctor_retrieve_user(self) -> None:
        """Verify that DOCTOR users only see basic user fields for one user."""
        # Create users
        users = UserFactory.create_batch(3)
        response = self.client.get(f'{self.url}{users[1].id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(users[1].username, response.data.get('username'))


class UsersPatientAPITestCase(APITestCase):
    """Users with PATIENT role API test case"""

    def setUp(self) -> None:
        # Authenticate user PATIENT
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/users/'

    def test_user_patient_create_users(self):
        """Verify that an PATIENT user can not create users"""
        response = self.client.post(self.url, USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 1)

    def test_user_patient_list_users(self) -> None:
        """Verify that a patient user cannot list users"""
        # Users in DB must be 1
        self.assertEqual(User.objects.count(), 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_patient_retrieve_user(self) -> None:
        """Verify that patient users can not retrieve users"""
        # Create users
        users = UserFactory.create_batch(3)
        response = self.client.get(f'{self.url}{users[1].id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UsersAPITestCase(APITestCase):
    """Users API test case"""

    def setUp(self) -> None:
        # Authenticate user PATIENT
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/users/'

    def test_my_profile(self) -> None:
        """Obtain the profile of the logged in user"""
        response = self.client.get(f'{self.url}me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), self.user.first_name, )

    def test_update_profile(self) -> None:
        """Verify that the user can update his profile"""
        data = {

        }
        response = self.client.post(f'{self.url}profile/', USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('first_name'), USER_DATA.get('first_name'))

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
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertContains(response, self.user.role, status_code=status.HTTP_201_CREATED)
