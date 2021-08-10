"""Appointment serializers"""

from rest_framework import serializers, fields

from apps.accounts.api.serializers.users import UserListRelatedSerializer
from apps.appointments.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment serializer
    Used by user ADMIN
    """

    type = fields.MultipleChoiceField(choices=Appointment.APPOINTMENT_TYPE_CHOICES)

    class Meta:
        model = Appointment
        exclude = ('user',)

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
    type = fields.MultipleChoiceField(choices=Appointment.APPOINTMENT_TYPE_CHOICES)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('start_date', 'end_date', 'doctor', 'created_at', 'updated_at')


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer"""

    user = UserListRelatedSerializer(read_only=True)
    doctor = UserListRelatedSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
