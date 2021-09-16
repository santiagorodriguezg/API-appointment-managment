"""Account serializers"""

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.utils import (
    clean_password2, delete_user_sessions, get_user_from_uidb64, password_reset_check_token
)


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
            raise AuthenticationFailed(detail='Usuario o contraseña incorrectos')

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
        user = User.objects.filter(username=value, is_active=True).first()
        if user is None:
            raise NotFound(detail='El usuario no está asignado a ninguna cuenta.')

        self.instance = user
        return value

    def save(self, **kwargs):
        """Send password reset email"""

        if self.instance.email is None:
            self.context['send_email'] = False
        else:
            send = self.send_password_reset_email()
            self.context['send_email'] = send == 1

        return self.instance

    def send_password_reset_email(self):
        """Send reset password link to given user."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.instance.id))
        token = PasswordResetTokenGenerator().make_token(self.instance)
        url = f'{settings.DEFAULT_DOMAIN}/accounts/password/reset/{uidb64}/{token}'
        template_prefix = 'accounts/email/password_reset_key'
        context = {'user': self.instance, 'password_reset_url': url}
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = " ".join(subject.splitlines()).strip()  # Remove superfluous line breaks
        content = render_to_string(f'{template_prefix}_message.html', context)
        msg = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [self.instance.email])
        msg.attach_alternative(content, "text/html")
        return msg.send()


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
        password_reset_check_token(user, data.get('token'))
        self.instance = user
        return clean_password2(self.instance, data)

    def save(self, **kwargs):
        """Update user´s password"""
        self.instance.set_password(self.validated_data['password2'])
        self.instance.save(update_fields=['password', 'updated_at'])
