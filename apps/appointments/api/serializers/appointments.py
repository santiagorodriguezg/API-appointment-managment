"""Appointment serializers"""

from rest_framework import serializers, fields

from apps.appointments.models import Appointment, AppointmentMultimedia
from apps.accounts.api.serializers.users import UserListRelatedSerializer
from apps.appointments.utils import validate_appointment_type, save_appointment_multimedia


class CustomMultipleChoiceField(fields.CharField):
    """Reads the appointment type options and represents it as a list."""

    def to_representation(self, value):
        return value.split(',')


class AppointmentMultimediaSerializer(serializers.ModelSerializer):
    """Appointment Multimedia Serializer"""

    class Meta:
        model = AppointmentMultimedia
        fields = ('file',)


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment serializer
    Used by user ADMIN
    """

    multimedia = AppointmentMultimediaSerializer(many=True, required=False)
    type = CustomMultipleChoiceField()

    class Meta:
        model = Appointment
        fields = (
            'id', 'doctor', 'type', 'children', 'aggressor', 'description', 'audio', 'start_date', 'end_date',
            'multimedia',
        )
        read_only_fields = ('id',)

    def validate_type(self, value):
        return validate_appointment_type(value)

    def create(self, validated_data):
        """Assign the user who has the active session"""
        multimedia = None
        if 'multimedia' in validated_data:
            multimedia = validated_data['multimedia']
            validated_data.pop('multimedia')

        appointment = Appointment(**validated_data, user=self.context['user'])
        appointment.save()
        return save_appointment_multimedia(multimedia, appointment)


class AppointmentUserSerializer(serializers.ModelSerializer):
    """
    Appointment user serializer
    Used by user with role USER
    """

    multimedia = AppointmentMultimediaSerializer(many=True, required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type = CustomMultipleChoiceField()

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('start_date', 'end_date', 'doctor', 'created_at', 'updated_at')

    def validate_type(self, value):
        return validate_appointment_type(value)

    def create(self, validated_data):
        """Assign the user who has the active session"""
        multimedia = None
        if 'multimedia' in validated_data:
            multimedia = validated_data['multimedia']
            validated_data.pop('multimedia')

        appointment = Appointment(**validated_data)
        appointment.save()
        return save_appointment_multimedia(multimedia, appointment)


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer"""

    user = UserListRelatedSerializer(read_only=True)
    doctor = UserListRelatedSerializer(read_only=True)
    type = CustomMultipleChoiceField(read_only=True)
    multimedia = AppointmentMultimediaSerializer(read_only=True, many=True)

    class Meta:
        model = Appointment
        fields = '__all__'
