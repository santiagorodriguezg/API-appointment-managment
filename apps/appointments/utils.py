"""Appointments utilities"""

from rest_framework import serializers

from apps.accounts.models import User
from apps.appointments.models import Appointment, AppointmentMultimedia


class StringMultipleChoiceField(serializers.CharField):
    """Reads the appointment type options and represents it as a list."""

    def to_internal_value(self, data):
        """Validate appoint type field"""
        appointment_type_choices = [c[0] for c in Appointment.APPOINTMENT_TYPE_CHOICES]
        choices = list(set(data.split(',')))
        for c in choices:
            if c not in appointment_type_choices:
                raise serializers.ValidationError(detail=f'"{c}" no es una elección válida.', code='invalid_choice')
        return ','.join(choices)

    def to_representation(self, value):
        return value.split(',')


class DoctorsUsernameField(serializers.CharField):
    """
    It is used to represent the relationship with the users with doctor role using the `username` field.
    The values are passed as follows:

    doctors_username: username1,username2
    """

    default_error_messages = {
        'invalid_doctor_username': 'Los nombres de usuario de los doctores son inválidos.',
    }

    def to_internal_value(self, data):
        data = data.split(',')
        queryset = User.objects.filter(username__in=data, role=User.Type.DOCTOR)
        if not queryset.exists():
            self.fail('invalid_doctor_username')
        return queryset

    def to_representation(self, value):
        return value.split(',')


def save_appointment_multimedia(multimedia, appointment):
    """Save the files of the appointment in the database"""
    if multimedia:
        objs = []
        for media in multimedia:
            objs.append(AppointmentMultimedia(**media, appointment=appointment))
        AppointmentMultimedia.objects.bulk_create(objs)
    return appointment
