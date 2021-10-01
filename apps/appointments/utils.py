"""Appointments utilities"""

from rest_framework import serializers

from apps.appointments.models import Appointment, AppointmentMultimedia


def validate_appointment_type(value):
    """Validate appoint type field"""
    appointment_type_choices = [c[0] for c in Appointment.APPOINTMENT_TYPE_CHOICES]
    choices = list(set(value.split(',')))
    for c in choices:
        if c not in appointment_type_choices:
            raise serializers.ValidationError(detail=f'"{c}" no es una elección válida.', code='invalid_choice')
    return ','.join(choices)


def save_appointment_multimedia(multimedia, appointment):
    """Save the files of the appointment in the database"""
    if multimedia:
        for media in multimedia:
            AppointmentMultimedia.objects.create(**media, appointment=appointment)

    return appointment
