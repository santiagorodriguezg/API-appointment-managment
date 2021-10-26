"""Appointment serializers"""

from rest_framework import serializers

from apps.appointments.models import Appointment, AppointmentMultimedia
from apps.accounts.api.serializers.users import UserListRelatedSerializer
from apps.appointments.utils import StringMultipleChoiceField, DoctorsUsernameField, save_appointment_multimedia


class AppointmentMultimediaSerializer(serializers.ModelSerializer):
    """Appointment Multimedia Serializer"""

    file_name = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentMultimedia
        exclude = ('appointment',)

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1]


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment serializer
    Used by user ADMIN
    """

    type = StringMultipleChoiceField()
    doctors = UserListRelatedSerializer(read_only=True, many=True)
    multimedia = AppointmentMultimediaSerializer(many=True, required=False)
    doctors_username = DoctorsUsernameField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = (
            'id', 'doctors', 'type', 'children', 'aggressor', 'description', 'audio', 'start_date', 'end_date',
            'created_at', 'updated_at', 'multimedia', 'doctors_username',
        )

    def create(self, validated_data):
        multimedia = validated_data.pop('multimedia', None)
        doctors = validated_data.pop('doctors_username', None)
        appointment = Appointment.objects.create(**validated_data, user=self.context['user'])
        if doctors:
            appointment.doctors.set(doctors)
        return save_appointment_multimedia(multimedia, appointment)

    def update(self, instance, validated_data):
        """Update the user's appointment. Media files are not updated."""
        validated_data.pop('multimedia', None)
        doctors = validated_data.pop('doctors_username', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if doctors:
            instance.doctors.set(doctors)

        return instance


class AppointmentUserSerializer(serializers.ModelSerializer):
    """
    Appointment user serializer
    Used by user with role USER
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    multimedia = AppointmentMultimediaSerializer(many=True, required=False)
    type = StringMultipleChoiceField()
    doctors = UserListRelatedSerializer(read_only=True, many=True)

    class Meta:
        model = Appointment
        fields = (
            'id', 'user', 'doctors', 'type', 'children', 'aggressor', 'description', 'audio', 'created_at',
            'updated_at', 'multimedia',
        )

    def create(self, validated_data):
        multimedia = validated_data.pop('multimedia', None)
        appointment = Appointment.objects.create(**validated_data)
        return save_appointment_multimedia(multimedia, appointment)

    def update(self, instance, validated_data):
        """Update the user's appointment. Media files are not updated."""
        validated_data.pop('multimedia', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer"""

    user = UserListRelatedSerializer(read_only=True)
    type = StringMultipleChoiceField(read_only=True)
    doctors = UserListRelatedSerializer(read_only=True, many=True)
    multimedia = AppointmentMultimediaSerializer(read_only=True, many=True)

    class Meta:
        model = Appointment
        fields = '__all__'
