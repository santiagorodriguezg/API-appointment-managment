"""Appointments tests"""

import json

from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment
from tests.accounts.factories import UserFactory, UserAdminFactory, UserDoctorFactory
from tests.appointments.factories import (
    AppointmentFactory, AppointmentMultimediaIMGFactory, AppointmentMultimediaPDFactory
)
from tests.utils import API_ENDPOINT_V1, AccessTokenTest, delete_all_test_files


class AppointmentsAdminAPITestCase(APITestCase):
    """
    Appointments API test case.
    For ADMIN users only.
    """

    def setUp(self) -> None:
        # Authenticate user ADMIN
        self.user = UserAdminFactory()
        self.token = AccessTokenTest().for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.token)}')

    def tearDown(self) -> None:
        # Delete test files
        delete_all_test_files()

    def test_appointments_list(self) -> None:
        """
        Appointment List API View test case
        An ADMIN user can list appointments with all fields
        """
        doctors = UserDoctorFactory.create_batch(2)
        AppointmentFactory.create(doctors=(doctors[0],))
        AppointmentFactory.create(doctors=(doctors[1],))

        response = self.client.get(f'/{API_ENDPOINT_V1}/appointments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        appt = response.data.get('results')
        queryset = Appointment.objects.select_related('user').prefetch_related('doctors').order_by('-created_at')

        for i, a in enumerate(queryset):
            self.assertEqual(appt[i]['user']['username'], a.user.username)

            for j, o in enumerate(a.doctors.all()):
                self.assertEqual(appt[i]['doctors'][j]['username'], o.username)

    def test_create_appointment_by_user_admin(self) -> None:
        """Verify that an ADMIN user can create appointments"""
        doctors = UserDoctorFactory.create_batch(3)
        users = UserFactory.create_batch(2)
        appointment = AppointmentFactory.build()
        appointment_img_file = AppointmentMultimediaIMGFactory.build()
        appointment_pdf_file = AppointmentMultimediaPDFactory.build()

        url = f'/{API_ENDPOINT_V1}/users/{users[1].username}/appointments/'
        data = {
            'type': appointment.type,
            'audio': appointment.audio,
            'doctors_username': f'{doctors[0].username},{doctors[1].username}',
            'children': json.dumps(appointment.children),
            'aggressor': json.dumps(appointment.aggressor),
            'description': appointment.description,
            'start_date': appointment.start_date,
            'end_date': appointment.end_date,
            'multimedia[0]file': appointment_img_file.file,
            'multimedia[0]file_type': appointment_img_file.file_type,
            'multimedia[1]file': appointment_pdf_file.file,
            'multimedia[1]file_type': appointment_pdf_file.file_type,
        }

        response = self.client.post(url, data, format='multipart')
        multimedia = response.data.get('multimedia')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertIsNone(response.data.get('user'))
        self.assertEqual(response.data['doctors'][0]['username'], doctors[0].username)
        self.assertEqual(multimedia[0]['file_name'], appointment_img_file.file.name)
        self.assertEqual(multimedia[1]['file_name'], appointment_pdf_file.file.name)

    def test_list_appointments_by_user_admin(self) -> None:
        """An ADMIN user can list all appointments with all fields"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        AppointmentFactory()
        AppointmentFactory(user=user)
        AppointmentFactory(user=user, doctors=(doctor,))

        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/'
        response = self.client.get(url)
        appointments = response.data.get('results')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = (Appointment.objects.select_related('user').prefetch_related('doctors')
                    .filter(user=user).order_by('-created_at'))

        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i]['user']['username'], a.user.username)

            if not a.doctors.exists():
                self.assertListEqual(appointments[i]['doctors'], [])
                continue

            for j, o in enumerate(a.doctors.all()):
                self.assertEqual(appointments[i]['doctors'][j]['username'], o.username)

    def test_retrieve_appointment_by_user_admin(self) -> None:
        """Retrieve appointment from the user given Id"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        AppointmentFactory(user=user)
        appointment = AppointmentFactory(user=user, doctors=(doctor,))

        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/{appointment.id}/'
        response = self.client.get(url)
        appointment_res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(user=user).count(), 2)

        self.assertEqual(appointment_res['id'], appointment.id)
        self.assertEqual(appointment_res['user']['username'], user.username)
        self.assertEqual(appointment_res['doctors'][0]['username'], doctor.username)

    def test_update_appointment_by_user_admin(self) -> None:
        """Update appointment for given id"""
        doctors = UserDoctorFactory.create_batch(2)
        users = UserFactory.create_batch(2)
        AppointmentFactory(user=users[0])
        appointment = AppointmentFactory(user=users[0], doctors=(doctors[0],))

        new_appointment = AppointmentFactory.build()
        data = {
            'type': new_appointment.type,
            'audio': new_appointment.audio,
            'doctors_username': f'{doctors[1].username}',
            'children': json.dumps(new_appointment.children),
            'aggressor': json.dumps(new_appointment.aggressor),
            'description': new_appointment.description,
            'start_date': new_appointment.start_date,
            'end_date': new_appointment.end_date,
        }

        url = f'/{API_ENDPOINT_V1}/users/{users[0].username}/appointments/{appointment.id}/'
        response = self.client.put(url, data, format='multipart')

        queryset = Appointment.objects.get(pk=appointment.id, user=users[0])

        self.assertEqual(appointment.user_id, queryset.user_id)
        self.assertEqual(response.data['id'], appointment.id)
        self.assertEqual(response.data['doctors'][0]['username'], doctors[1].username)
        self.assertEqual(response.data['type'][0], new_appointment.type)


class AppointmentsDoctorAPITestCase(APITestCase):
    """
    Appointments API test case.
    For DOCTOR users only.
    """

    def setUp(self) -> None:
        # Authenticate user DOCTOR
        UserAdminFactory()
        self.user = UserDoctorFactory()
        self.token = AccessTokenTest().for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.token)}')
        self.url = f'/{API_ENDPOINT_V1}/users/{self.user.username}/appointments/'

    def tearDown(self) -> None:
        # Delete test files
        delete_all_test_files()

    def test_create_appointment_by_user_doctor(self) -> None:
        """Verify that an DOCTOR user can not create appointments"""
        UserDoctorFactory()
        users = UserFactory.create_batch(2)
        appointment = AppointmentFactory.build()
        data = {
            'type': appointment.type,
            'audio': appointment.audio,
            'description': appointment.description,
        }

        # Crear cita asociada al perfil del doctor
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 0)

        # Crear cita asociada al perfil de un usuario
        url = f'/{API_ENDPOINT_V1}/users/{users[1].username}/appointments/'
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_list_appointments_by_user_doctor(self) -> None:
        """Verify that a doctor can only list his appointments"""
        user = UserFactory()
        AppointmentFactory.create_batch(2)
        AppointmentFactory.create_batch(2, doctors=(self.user,))

        # Listar citas asociadas al perfil del doctor
        response = self.client.get(self.url)
        appointments = response.data.get('results')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = (Appointment.objects.select_related('user').prefetch_related('doctors')
                    .filter(doctors=self.user).order_by('-created_at'))
        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i]['user']['username'], a.user.username)

            for j, o in enumerate(a.doctors.all()):
                self.assertEqual(appointments[i]['doctors'][j]['username'], o.username)

        # Listar citas asociadas al perfil de otro usuario
        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_appointment_by_user_doctor(self) -> None:
        """Retrieve appointment from the user given Id"""
        user = UserFactory()
        AppointmentFactory.create_batch(2)
        appointment = AppointmentFactory(user=user, doctors=(self.user,))

        url = f'{self.url}{appointment.id}/'
        response = self.client.get(url)
        appointment_res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(doctors=self.user).count(), 1)
        self.assertEqual(appointment_res['id'], appointment.id)
        self.assertEqual(appointment_res['user']['username'], user.username)
        self.assertEqual(appointment_res['doctors'][0]['username'], self.user.username)

        # Obtener cita asociadas al perfil de otro usuario
        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/{appointment.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_appointment_by_user_doctor(self) -> None:
        """Update appointment for given id"""
        user = UserFactory()
        AppointmentFactory(user=user)
        appointment = AppointmentFactory(user=user, doctors=(self.user,))

        new_appointment = AppointmentFactory.build()
        data = {
            'type': new_appointment.type,
            'audio': new_appointment.audio,
            'description': new_appointment.description,
        }

        url = f'{self.url}{appointment.id}/'
        response = self.client.put(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.filter(doctors=self.user).count(), 1)

        # Actualizar cita asociada al perfil de otro usuario
        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/{appointment.id}/'
        response = self.client.put(url, data, format='multipart')

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
        self.token = AccessTokenTest().for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.token)}')
        self.url = f'/{API_ENDPOINT_V1}/users/{self.user.username}/appointments/'

    def tearDown(self) -> None:
        # Delete test files
        delete_all_test_files()

    def test_create_appointment_by_user_patient(self) -> None:
        """Verify that an patient user can create appointments"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        appointment = AppointmentFactory.build()
        appointment_img_file = AppointmentMultimediaIMGFactory.build()
        appointment_pdf_file = AppointmentMultimediaPDFactory.build()

        data = {
            'type': appointment.type,
            'audio': appointment.audio,
            'doctors': f'{doctor.username}',
            'children': json.dumps(appointment.children),
            'aggressor': json.dumps(appointment.aggressor),
            'description': appointment.description,
            'start_date': appointment.start_date,
            'end_date': appointment.end_date,
            'multimedia[0]file': appointment_img_file.file,
            'multimedia[0]file_type': appointment_img_file.file_type,
            'multimedia[1]file': appointment_pdf_file.file,
            'multimedia[1]file_type': appointment_pdf_file.file_type,
        }

        # Crear cita asociada al perfil del usuario
        response = self.client.post(self.url, data, format='multipart')
        multimedia = response.data.get('multimedia')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertIsNone(response.data.get('user'))
        self.assertIsNone(response.data.get('doctor'))
        self.assertEqual(multimedia[0]['file_name'], appointment_img_file.file.name)
        self.assertEqual(multimedia[1]['file_name'], appointment_pdf_file.file.name)

        # Crear cita asociada al perfil de otro usuario
        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/'
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_list_appointments_by_user_patient(self) -> None:
        """Verify that a patient can only list his appointments"""
        doctor = UserDoctorFactory()
        AppointmentFactory(user=self.user)
        AppointmentFactory(user=self.user, doctors=(doctor,))
        AppointmentFactory.create_batch(2)

        response = self.client.get(self.url)
        appointments = response.data.get('results')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

        queryset = (Appointment.objects.select_related('user').prefetch_related('doctors')
                    .filter(user=self.user).order_by('-created_at'))
        for i, a in enumerate(queryset):
            self.assertEqual(appointments[i]['user']['username'], a.user.username)

            if not a.doctors.exists():
                self.assertEqual(appointments[i]['doctors'], [])
                continue

            for j, o in enumerate(a.doctors.all()):
                self.assertEqual(appointments[i]['doctors'][j]['username'], o.username)

        # Listar citas asociadas al perfil de otro usuario
        url = f'/{API_ENDPOINT_V1}/users/{doctor.username}/appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_appointment_by_user_patient(self) -> None:
        """Retrieve appointment from the user given Id"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        user_appt = AppointmentFactory(user=user)
        appointment = AppointmentFactory(user=self.user, doctors=(doctor,))

        url = f'{self.url}{appointment.id}/'
        response = self.client.get(url)
        appointment_res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(user=self.user).count(), 1)
        self.assertEqual(appointment_res['id'], appointment.id)
        self.assertEqual(appointment_res['user']['username'], self.user.username)
        self.assertEqual(appointment_res['doctors'][0]['username'], doctor.username)

        # Obtener citas asociadas al perfil de otro usuario
        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/{user_appt.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_appointment_by_user_patient(self) -> None:
        """Update appointment for given id"""
        doctor = UserDoctorFactory()
        user = UserFactory()
        user_appt = AppointmentFactory(user=user, doctors=(doctor,))
        appointment = AppointmentFactory(user=self.user, start_date=None, end_date=None)

        new_appointment = AppointmentFactory.build()
        data = {
            'type': new_appointment.type,
            'audio': new_appointment.audio,
            'doctors_username': f'{doctor.username}',
            'children': json.dumps(new_appointment.children),
            'aggressor': json.dumps(new_appointment.aggressor),
            'description': new_appointment.description,
        }

        url = f'{self.url}{appointment.id}/'
        response = self.client.put(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.filter(user=self.user).count(), 1)
        self.assertEqual(response.data['type'][0], new_appointment.type)
        self.assertListEqual(response.data['doctors'], [])
        self.assertListEqual(response.data['multimedia'], [])

        # Actualizar cita asociada al perfil de otro usuario
        data['user'] = self.user.id
        data['doctors_username'] = ''

        url = f'/{API_ENDPOINT_V1}/users/{user.username}/appointments/{user_appt.id}/'
        response = self.client.put(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
