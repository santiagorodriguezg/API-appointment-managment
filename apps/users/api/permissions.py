"""User permissions"""

from rest_framework.permissions import BasePermission

from apps.users.models import User


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
