"""Appointments tests"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment
from tests.appointments.factory import AppointmentFactory, APPOINTMENT_FACTORY_DICT
from tests.users.factory import UserFactory, UserAdminFactory, TokenFactory, UserDoctorFactory


class AppointmentsAdminAPITestCase(APITestCase):
    """
    Appointments API test case.
    For ADMIN users only.
    """

    def setUp(self) -> None:
        # Authenticate user ADMIN
        self.user = UserAdminFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_create_appointment_by_user_admin(self) -> None:
        """Verify that an ADMIN user can create appointments"""
        doctors = UserDoctorFactory.create_batch(2)
        users = UserFactory.create_batch(2)
        APPOINTMENT_FACTORY_DICT.pop('user')
        APPOINTMENT_FACTORY_DICT['doctor'] = doctors[0].id

        url = f'/users/{users[1].username}/appointments/'
        response = self.client.post(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(response.data.get('doctor'), APPOINTMENT_FACTORY_DICT.get('doctor'))
        self.assertIsNone(response.data.get('user'))

    def test_list_appointments_by_user_admin(self) -> None:
        """An ADMIN user can list all appointments with all fields"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        AppointmentFactory()
        AppointmentFactory(user=user)
        AppointmentFactory(user=user, doctor=doctor)

        url = f'/users/{user.username}/appointments/'
        response = self.client.get(url)
        res = response.data.get('results')
        appointments = res.get('appointments')
        user_res = res.get('user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(user_res.get('id'), user.id)

        queryset = Appointment.objects.select_related('user', 'doctor').filter(user=user)
        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i].get('user'), a.user.id)
            if a.doctor is None:
                self.assertIsNone(appointments[i].get('doctor'))
                continue
            self.assertEqual(appointments[i].get('doctor'), a.doctor.id)


class AppointmentsDoctorAPITestCase(APITestCase):
    """
    Appointments API test case.
    For DOCTOR users only.
    """

    def setUp(self) -> None:
        # Authenticate user DOCTOR
        self.user = UserDoctorFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/users/{self.user.username}/appointments/'

    def test_create_appointment_by_user_doctor(self) -> None:
        """Verify that an DOCTOR user can not create appointments"""
        doctor = UserDoctorFactory()
        users = UserFactory.create_batch(2)
        APPOINTMENT_FACTORY_DICT['user'] = users[1].id
        APPOINTMENT_FACTORY_DICT['doctor'] = doctor.id

        # Crear cita asociada al perfil de un usuario
        response = self.client.post(self.url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 0)

        # Crear cita asociada al perfil del doctor
        url = f'/users/{users[1].username}/appointments/'
        response = self.client.post(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_list_appointments_by_user_doctor(self) -> None:
        """Verify that a patient can only list his appointments"""
        user = UserFactory()
        AppointmentFactory.create_batch(2)
        AppointmentFactory.create_batch(2, doctor=self.user)

        # Listar citas asociadas al perfil del doctor
        response = self.client.get(self.url)
        res = response.data.get('results')
        user_res = res.get('user')
        appointments = res.get('appointments')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(user_res.get('id'), self.user.id)

        queryset = Appointment.objects.select_related('user', 'doctor').filter(doctor=self.user)
        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i].get('user'), a.user.id)
            self.assertEqual(appointments[i].get('doctor'), a.doctor.id)

        # Listar citas asociadas al perfil de otro usuario
        url = f'/users/{user.username}/appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AppointmentsPatientAPITestCase(APITestCase):
    """
    Appointments API test case.
    For PATIENT users only.
    """

    def setUp(self) -> None:
        # Authenticate user DOCTOR
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/users/{self.user.username}/appointments/'

    def test_create_appointment_by_user_patient(self) -> None:
        """Verify that an patient user can create appointments"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        APPOINTMENT_FACTORY_DICT.pop('user')
        APPOINTMENT_FACTORY_DICT['doctor'] = doctor.id

        # Crear cita asociada al perfil del usuario
        response = self.client.post(self.url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertIsNone(response.data.get('start_time'))
        self.assertIsNone(response.data.get('end_time'))
        self.assertIsNone(response.data.get('user'))
        self.assertIsNone(response.data.get('doctor'))

        # Crear cita asociada al perfil de otro usuario
        url = f'/users/{user.username}/appointments/'
        response = self.client.post(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_list_appointments_by_user_patient(self) -> None:
        """Verify that a patient can only list his appointments"""
        doctor = UserDoctorFactory()
        AppointmentFactory(user=self.user)
        AppointmentFactory(user=self.user, doctor=doctor)
        AppointmentFactory.create_batch(2)

        response = self.client.get(self.url)
        res = response.data.get('results')
        user_res = res.get('user')
        appointments = res.get('appointments')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(user_res.get('id'), self.user.id)

        queryset = Appointment.objects.select_related('user', 'doctor').filter(user=self.user)
        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i].get('user'), a.user.id)
            if a.doctor is None:
                self.assertIsNone(appointments[i].get('doctor'))
                continue
            self.assertEqual(appointments[i].get('doctor'), a.doctor.id)

        # Listar citas asociadas al perfil de otro usuario
        url = f'/users/{doctor.username}/appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
