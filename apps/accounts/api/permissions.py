"""Accounts permissions"""
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

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


class IsAdminOrPatientUser(BasePermission):
    """
    Allows access only to ADMIN or PATIENT users.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff or user.role == User.Type.USER:
                return True
        return False


class IsAccountOwnerOrAdminUser(BasePermission):
    """Allow access only to objects owned by the requesting user or ADMIN users."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            user_db = User.objects.filter(username=request.parser_context['kwargs']['username']).only('id').first()
            if user_db is None:
                raise NotFound(detail='Usuario no encontrado.')
            return user.id == user_db.id or user.role == User.Type.ADMIN
        return False
