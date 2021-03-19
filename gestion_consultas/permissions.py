"""Permissions"""

from rest_framework.permissions import BasePermission

from gestion_consultas.utils import UserType


class IsAdminOrDoctorUser(BasePermission):
    """
    Allows access only to ADMIN or DOCTOR users.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff or user.user_type == UserType.DOCTOR:
                return True
        return False
