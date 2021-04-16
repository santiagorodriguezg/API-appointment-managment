"""Accounts utilities"""

from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.accounts.models import User


def delete_user_sessions(user, token):
    """Delete the authentication token and user sessions."""

    all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    if all_sessions.exists():
        for session in all_sessions:
            session_data = session.get_decoded()
            session_user = session_data.get('_auth_user_id')
            if session_user:
                if user.id == int(session_user):
                    session.delete()
    token.delete()


def clean_password2(instance, data):
    """Verify passwords match"""

    password1 = data.get("password")
    password2 = data.get("password2")
    if password1 and password2 and password1 != password2:
        raise serializers.ValidationError(
            {'password2': 'Las contraseñas ingresadas no coinciden'}, code='password_mismatch',
        )
    try:
        password_validation.validate_password(password2, instance)
    except ValidationError as error:
        raise serializers.ValidationError({'password2': error.messages}, code='password2')

    return data


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


def generate_token(user, token_type):
    """Create JWT token"""
    exp_date = timezone.now() + timedelta(hours=settings.ACCOUNT_EMAIL_PASSWORD_RESET_EXPIRE_HOURS)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'type': token_type
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS384")


def verify_token(token):
    """
    Verify token is valid.
    :param token: JWT token
    :return: JWT payload
    """
    invalid_token = serializers.ValidationError('El enlace para restablecer la contraseña es invalido.')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS384'])
    except jwt.ExpiredSignatureError:
        raise serializers.ValidationError('El enlace para restablecer la contraseña ha expirado.')
    except jwt.PyJWTError:
        raise invalid_token

    if payload['type'] != 'password_reset':
        raise invalid_token

    return payload
