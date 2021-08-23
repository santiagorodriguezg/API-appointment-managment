"""Accounts utilities"""

from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.models import User


def delete_user_sessions(user):
    """Delete the authentication token and user sessions."""

    all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    if all_sessions.exists():
        for session in all_sessions:
            session_data = session.get_decoded()
            session_user = session_data.get('_auth_user_id')
            if session_user:
                if user.id == int(session_user):
                    session.delete()


def clean_password2(instance, data):
    """Verify passwords match"""

    password1 = data.get("password")
    password2 = data.get("password2")
    if password1 and password2 and password1 != password2:
        raise serializers.ValidationError(
            {'password': 'Las contraseñas ingresadas no coinciden'}, code='password_mismatch',
        )
    try:
        password_validation.validate_password(password2, instance)
    except ValidationError as error:
        raise serializers.ValidationError({'password': error.messages}, code='password2')

    return data


def get_user_from_uidb64(uidb64):
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        user = None
    return user


def password_reset_check_token(user, token):
    if not PasswordResetTokenGenerator().check_token(user, token):
        raise AuthenticationFailed(detail="El token no es válido, solicite uno nuevo")


def generate_token(user, token_type):
    """Create JWT token"""
    exp_date = timezone.now() + timedelta(minutes=settings.ACCOUNT_EMAIL_PASSWORD_RESET_EXPIRE_MINUTES)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'token_type': token_type
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

    if payload['token_type'] != 'password_reset':
        raise invalid_token

    return payload
