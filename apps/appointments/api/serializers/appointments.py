"""Appointments serializers"""

from rest_framework import serializers

from apps.appointments.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Appointment serializer"""

    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Appointment
        # fields = '__all__'
        exclude = ('user',)

    # def update(self, instance, validated_data):
    #     """Do not allow editing of the user who created the appointment"""
    #     validated_data.pop('user')
    #     return super(AppointmentCreateSerializer, self).update(instance, validated_data)
    def create(self, validated_data):
        appointment = Appointment(**validated_data, user=self.context['user'])
        appointment.save()
        return appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer"""

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentUserSerializer(serializers.ModelSerializer):
    """
    Appointment user serializer
    Create an appointment for a user with role USER
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('start_time', 'end_time', 'doctor', 'created_at', 'updated_at')
