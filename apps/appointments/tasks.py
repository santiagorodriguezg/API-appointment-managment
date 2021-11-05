"""Appointments Celery tasks"""
from django.conf import settings
from celery import shared_task

from apps.accounts.models import User
from apps.appointments.models import Appointment
from gestion_consultas.utils import send_email


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 2})
def send_doctor_assignment_notification(doctors_pks, user_admin_pk, appointment_pk):
    """Sends an email to users with a doctor role that has been assigned to an appointment"""
    doctors = User.objects.filter(pk__in=doctors_pks)
    user_admin = User.objects.get(pk=user_admin_pk)
    appointment = Appointment.objects.get(pk=appointment_pk)

    for doctor in doctors:
        context = {
            'user': doctor,
            'user_admin': user_admin,
            'appointment': appointment,
            'appointments_historic_url': f'{settings.CLIENT_DOMAIN}/appointments/historic'
        }
        send_email(doctor.email, 'accounts/email/doctor_assignment_notification', context)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 2})
def send_admin_email_new_appointment(user_patient_pk, appointment_pk):
    """Send email to administrator users when a new appointment is created"""
    admins = User.objects.filter(role=User.Type.ADMIN, is_active=True)
    user_patient = User.objects.get(pk=user_patient_pk)
    appointment = Appointment.objects.get(pk=appointment_pk)

    for admin in admins:
        context = {
            'user': admin,
            'user_patient': user_patient,
            'appointment': appointment,
            'user_patient_url_detail': f'{settings.CLIENT_DOMAIN}/users/{user_patient.username}',
            'appointments_historic_url': f'{settings.CLIENT_DOMAIN}/appointments/historic'
        }
        send_email(admin.email, 'accounts/email/new_appointment', context)
