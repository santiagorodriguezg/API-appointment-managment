"""Groups and user permissions"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from apps.appointments.models import Appointment
from apps.chats.models import Room, Message


def get_content_type(model):
    """Get model content type"""
    return ContentType.objects.get_for_model(model)


def create_permissions(user_class, user):
    """
    Create permissions for users
    :param user_class: User class
    :param user: User instance
    :return: None
    """
    # Get or create groups
    user_group, created_ug = Group.objects.get_or_create(name='Users')
    doctor_group, created_dg = Group.objects.get_or_create(name='Doctors')

    if user.role == user_class.Type.ADMIN:
        if created_dg and created_ug:
            # Get permissions
            qs = Permission.objects.order_by('id')
            user_perms = qs.filter(content_type=get_content_type(user_class))
            appointment_perms = qs.filter(content_type=get_content_type(Appointment), codename__endswith='from_me')
            room_perms = qs.filter(content_type=get_content_type(Room))
            message_perms = qs.filter(content_type=get_content_type(Message))

            permissions_user = [
                user_perms[1], user_perms[3], *appointment_perms[:2], appointment_perms[3], room_perms[0],
                room_perms[3], *message_perms
            ]
            permissions_doctor = [
                user_perms[1], user_perms[3], appointment_perms[3], room_perms[0], room_perms[3], *message_perms
            ]
            # Add permissions to group
            user_group.permissions.set(permissions_user)
            doctor_group.permissions.set(permissions_doctor)

    elif user.role == user_class.Type.DOCTOR:
        doctor_group.user_set.add(user)
    else:
        user_group.user_set.add(user)
