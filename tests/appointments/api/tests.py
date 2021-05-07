"""Appointments tests"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment
from tests.accounts.factories import UserFactory, UserAdminFactory, TokenFactory, UserDoctorFactory
from tests.appointments.factories import AppointmentFactory, APPOINTMENT_FACTORY_DICT
from tests.utils import API_VERSION_V1


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

    def test_appointments_list(self) -> None:
        """
        Appointment List API View test case
        An ADMIN user can list appointments with all fields
        """
        doctor = UserDoctorFactory()
        AppointmentFactory.create_batch(2, doctor=doctor)

        response = self.client.get(f'/{API_VERSION_V1}/appointments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        appt = response.data.get('results')
        queryset = Appointment.objects.select_related('user', 'doctor').all()
        for i, a in enumerate(queryset):
            self.assertEqual(appt[i]['user']['username'], a.user.username)
            self.assertEqual(appt[i]['doctor']['username'], a.doctor.username)

    def test_create_appointment_by_user_admin(self) -> None:
        """Verify that an ADMIN user can create appointments"""
        doctors = UserDoctorFactory.create_batch(2)
        users = UserFactory.create_batch(2)
        APPOINTMENT_FACTORY_DICT.pop('user')
        APPOINTMENT_FACTORY_DICT['doctor'] = doctors[0].id

        url = f'/{API_VERSION_V1}/users/{users[1].username}/appointments/'
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

        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/'
        response = self.client.get(url)
        res = response.data.get('results')
        appointments = res.get('appointments')
        user_res = res.get('user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(user_res.get('id'), user.id)

        queryset = Appointment.objects.select_related('user', 'doctor').filter(user=user)
        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i]['user']['username'], a.user.username)
            if a.doctor is None:
                self.assertIsNone(appointments[i].get('doctor'))
                continue
            self.assertEqual(appointments[i]['doctor']['username'], a.doctor.username)

    def test_retrieve_appointment_by_user_admin(self) -> None:
        """Retrieve appointment from the user given Id"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        AppointmentFactory(user=user)
        appointment = AppointmentFactory(user=user, doctor=doctor)

        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/{appointment.id}/'
        response = self.client.get(url)
        appointment_res = response.data.get('appointment')
        user_res = response.data.get('user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(user=user).count(), 2)
        self.assertEqual(user_res.get('id'), user.id)
        self.assertEqual(appointment_res.get('id'), appointment.id)
        self.assertEqual(appointment_res['user']['username'], user.username)
        self.assertEqual(appointment_res['doctor']['username'], doctor.username)

    def test_update_appointment_by_user_admin(self) -> None:
        """Update appointment for given id"""
        doctors = UserDoctorFactory.create_batch(2)
        users = UserFactory.create_batch(2)
        AppointmentFactory(user=users[0])
        appointment = AppointmentFactory(user=users[0], doctor=doctors[0])

        APPOINTMENT_FACTORY_DICT['user'] = users[1].id
        APPOINTMENT_FACTORY_DICT['doctor'] = doctors[1].id

        url = f'/{API_VERSION_V1}/users/{users[0].username}/appointments/{appointment.id}/'
        response = self.client.put(url, APPOINTMENT_FACTORY_DICT, format='json')

        queryset = Appointment.objects.get(pk=appointment.id, user=users[0])

        self.assertEqual(appointment.user_id, queryset.user_id)
        self.assertEqual(response.data.get('id'), appointment.id)
        self.assertEqual(response.data.get('doctor'), doctors[1].id)


class AppointmentsDoctorAPITestCase(APITestCase):
    """
    Appointments API test case.
    For DOCTOR users only.
    """

    def setUp(self) -> None:
        # Authenticate user DOCTOR
        UserAdminFactory()
        self.user = UserDoctorFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/{API_VERSION_V1}/users/{self.user.username}/appointments/'

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
        url = f'/{API_VERSION_V1}/users/{users[1].username}/appointments/'
        response = self.client.post(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_list_appointments_by_user_doctor(self) -> None:
        """Verify that a doctor can only list his appointments"""
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
            self.assertEqual(appointments[i]['user']['username'], a.user.username)
            self.assertEqual(appointments[i]['doctor']['username'], a.doctor.username)

        # Listar citas asociadas al perfil de otro usuario
        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_appointment_by_user_doctor(self) -> None:
        """Retrieve appointment from the user given Id"""
        user = UserFactory()
        AppointmentFactory.create_batch(2)
        appointment = AppointmentFactory(user=user, doctor=self.user)

        url = f'{self.url}{appointment.id}/'
        response = self.client.get(url)
        appointment_res = response.data.get('appointment')
        user_res = response.data.get('user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(doctor=self.user).count(), 1)
        self.assertEqual(user_res.get('id'), self.user.id)
        self.assertEqual(appointment_res.get('id'), appointment.id)
        self.assertEqual(appointment_res['user']['username'], user.username)
        self.assertEqual(appointment_res['doctor']['username'], self.user.username)

        # Obtener cita asociadas al perfil de otro usuario
        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/{appointment.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_appointment_by_user_doctor(self) -> None:
        """Update appointment for given id"""
        users = UserFactory.create_batch(2)
        AppointmentFactory(user=users[0])
        appointment = AppointmentFactory(user=users[0], doctor=self.user)

        APPOINTMENT_FACTORY_DICT['user'] = users[1].id

        url = f'{self.url}{appointment.id}/'
        response = self.client.put(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.filter(doctor=self.user).count(), 1)

        # Actualizar cita asociada al perfil de otro usuario
        url = f'/{API_VERSION_V1}/users/{users[0].username}/appointments/{appointment.id}/'
        response = self.client.put(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AppointmentsPatientAPITestCase(APITestCase):
    """
    Appointments API test case.
    For PATIENT users only.
    """

    def setUp(self) -> None:
        # Authenticate user PATIENT
        UserAdminFactory()
        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = f'/{API_VERSION_V1}/users/{self.user.username}/appointments/'

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
        self.assertIsNone(response.data.get('start_date'))
        self.assertIsNone(response.data.get('end_date'))
        self.assertIsNone(response.data.get('user'))
        self.assertIsNone(response.data.get('doctor'))

        # Crear cita asociada al perfil de otro usuario
        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/'
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
            self.assertEqual(appointments[i]['user']['username'], a.user.username)
            if a.doctor is None:
                self.assertIsNone(appointments[i].get('doctor'))
                continue
            self.assertEqual(appointments[i]['doctor']['username'], a.doctor.username)

        # Listar citas asociadas al perfil de otro usuario
        url = f'/{API_VERSION_V1}/users/{doctor.username}/appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_appointment_by_user_patient(self) -> None:
        """Retrieve appointment from the user given Id"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        user_appt = AppointmentFactory(user=user)
        appointment = AppointmentFactory(user=self.user, doctor=doctor)

        url = f'{self.url}{appointment.id}/'
        response = self.client.get(url)
        appointment_res = response.data.get('appointment')
        user_res = response.data.get('user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(user=self.user).count(), 1)
        self.assertEqual(user_res.get('id'), self.user.id)
        self.assertEqual(appointment_res.get('id'), appointment.id)
        self.assertEqual(appointment_res['user']['username'], self.user.username)
        self.assertEqual(appointment_res['doctor']['username'], doctor.username)

        # Obtener citas asociadas al perfil de otro usuario
        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/{user_appt.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_appointment_by_user_patient(self) -> None:
        """Update appointment for given id"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        user_appt = AppointmentFactory(user=user, doctor=doctor)
        appointment = AppointmentFactory(user=self.user, start_date=None, end_date=None)

        APPOINTMENT_FACTORY_DICT['doctor'] = doctor.id

        url = f'{self.url}{appointment.id}/'
        response = self.client.put(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(user=self.user).count(), 1)
        self.assertIsNone(response.data.get('start_date'))
        self.assertIsNone(response.data.get('end_date'))
        self.assertIsNone(response.data.get('doctor'))

        # Actualizar cita asociada al perfil de otro usuario
        APPOINTMENT_FACTORY_DICT['user'] = self.user.id
        APPOINTMENT_FACTORY_DICT['doctor'] = None

        url = f'/{API_VERSION_V1}/users/{user.username}/appointments/{user_appt.id}/'
        response = self.client.put(url, APPOINTMENT_FACTORY_DICT, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
