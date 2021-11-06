"""Account serializers"""

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.utils import (
    clean_password2, delete_user_sessions, get_user_from_uidb64, check_password_reset_token, validate_username,
    generate_password_reset_link
)
from gestion_consultas.utils import send_email


class SignupSerializer(serializers.ModelSerializer):
    """
    User sign up serializer.
    Handle sign up data validation and user creation.
    """

    password2 = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'identification_type', 'identification_number', 'email', 'phone',
            'city', 'neighborhood', 'address', 'password', 'password2'
        )

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def create(self, validated_data):
        """Handle user with user role and token creation"""

        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.role = User.Type.USER
        user.last_login = timezone.now()
        user.save()
        refresh = user.get_tokens()  # Get tokens
        self.context['refresh'] = str(refresh)
        self.context['access'] = str(refresh.access_token)
        return user


class LoginSerializer(serializers.Serializer):
    """
    User login serializer.
    Handle the login request data.
    """

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Check credentials"""

        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise AuthenticationFailed(detail='Usuario o contraseña incorrectos.')

        if not user.is_active:
            raise AuthenticationFailed(detail='Su cuenta ha sido desactivada.')

        # if not user.is_verified:
        #     raise serializers.ValidationError('Account is not active yet :(')

        update_last_login(None, user)  # Update the last login date
        delete_user_sessions(user)  # Delete users sessions
        refresh = user.get_tokens()  # Get tokens
        self.context['refresh'] = str(refresh)
        self.context['access'] = str(refresh.access_token)
        self.instance = user
        return data


class LogoutSerializer(serializers.Serializer):
    """User logout serializer"""

    refresh = serializers.CharField(required=True)

    def save(self, **kwargs):
        try:
            token = self.validated_data['refresh']
            RefreshToken(token).blacklist()

            # Delete users sessions
            decode_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user = User.objects.get(username=decode_jwt['user_username'])
            delete_user_sessions(user)
        except TokenError:
            raise serializers.ValidationError(
                {'errors': 'El token es inválido o ha expirado.'}, code='token_invalid'
            )


class PasswordResetEmailSerializer(serializers.Serializer):
    """
    Finds the user account given a username and send email reset password.
    """
    username = serializers.CharField()

    def validate_username(self, value):
        """Verify that the user account exists"""
        self.instance = validate_username(value)
        return value

    def save(self, **kwargs):
        """Send password reset email"""

        if self.instance.email is None:
            self.context['send_email'] = False
        else:
            template_context = {
                'user': self.instance,
                'password_reset_url': generate_password_reset_link(self.instance)
            }
            send = send_email(self.instance.email, 'accounts/email/password_reset_key', template_context)
            self.context['send_email'] = send == 1

        return self.instance


class PasswordResetCompleteSerializer(serializers.Serializer):
    """
    Update the user's password
    """
    password = serializers.CharField()
    password2 = serializers.CharField()
    token = serializers.CharField()
    uid = serializers.CharField()

    class Meta:
        fields = ['password', 'password2', 'token', 'uid']

    def validate(self, data):
        user = get_user_from_uidb64(data.get('uid'))
        check_password_reset_token(user, data.get('token'))
        self.instance = user
        return clean_password2(self.instance, data)

    def save(self, **kwargs):
        """Update user´s password"""
        self.instance.set_password(self.validated_data['password2'])
        self.instance.save(update_fields=['password', 'updated_at'])
