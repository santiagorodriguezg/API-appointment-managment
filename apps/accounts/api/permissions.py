"""Accounts permissions"""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.accounts.models import User


class IsAdminOrDoctorUser(BasePermission):
    """
    Allows access only to ADMIN or DOCTOR users.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff or user.role == User.Type.DOCTOR:
                return True
        return False


def is_account_owner(request_user, username):
    """Allow access only to objects owned by the requesting user"""
    user_db = User.objects.filter(username=username).only('id').first()
    if user_db is None:
        raise NotFound(detail='Usuario no encontrado.')
    return request_user.id == user_db.id


def check_permissions(user, username, permission):
    """
    Verify that the user is a superuser, otherwise that the user is the owner of the resource, or has the necessary
    permissions.

    :param user: User request
    :param username: Username of url
    :param permission: Permission to access
    :return: None
    """
    if not user.is_superuser:
        if (
                is_account_owner(user, username) and not user.has_perm(f'{permission}_from_me') or
                not is_account_owner(user, username) and not user.has_perm(permission)
        ):
            raise PermissionDenied()
