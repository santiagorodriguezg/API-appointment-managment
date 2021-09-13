"""Appointment serializers"""

from rest_framework import serializers, fields

from apps.accounts.api.serializers.users import UserListRelatedSerializer
from apps.appointments.models import Appointment


def validate_appointment_type(value):
    """Validate appoint type field"""
    appointment_type_choices = [c[0] for c in Appointment.APPOINTMENT_TYPE_CHOICES]
    choices = list(set(value.split(',')))
    for c in choices:
        if c not in appointment_type_choices:
            raise serializers.ValidationError(detail=f'"{c}" no es una elección válida.', code='invalid_choice')
    return ','.join(choices)


class CustomMultipleChoiceField(fields.CharField):
    """Reads the appointment type options and represents it as a list."""

    def to_representation(self, value):
        return value.split(',')


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment serializer
    Used by user ADMIN
    """

    type = CustomMultipleChoiceField()

    class Meta:
        model = Appointment
        exclude = ('user',)

    def validate_type(self, value):
        return validate_appointment_type(value)

    def create(self, validated_data):
        """Assign the user who has the active session"""
        appointment = Appointment(**validated_data, user=self.context['user'])
        appointment.save()
        return appointment


class AppointmentUserSerializer(serializers.ModelSerializer):
    """
    Appointment user serializer
    Used by user with role USER
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type = CustomMultipleChoiceField()

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('start_date', 'end_date', 'doctor', 'created_at', 'updated_at')

    def validate_type(self, value):
        return validate_appointment_type(value)


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer"""

    user = UserListRelatedSerializer(read_only=True)
    doctor = UserListRelatedSerializer(read_only=True)
    type = CustomMultipleChoiceField(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
