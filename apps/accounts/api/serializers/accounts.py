"""Account serializers"""

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.utils import clean_password2, delete_user_sessions, generate_token, verify_token


class SignUpSerializer(serializers.ModelSerializer):
    """
    User sign up serializer.
    Handle sign up data validation and user creation.
    """

    password2 = serializers.CharField(min_length=8)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

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
        refresh = self.get_token(user)  # Get tokens
        self.context['refresh'] = str(refresh)
        self.context['access'] = str(refresh.access_token)
        return user


class LoginSerializer(serializers.Serializer):
    """
    User login serializer.
    Handle the login request data.
    """

    username = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=64)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, data):
        """Check credentials"""

        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError({
                'errors': 'Usuario o contraseña incorrectos'
            }, code='authorization')

        # if not user.is_verified:
        #     raise serializers.ValidationError('Account is not active yet :(')

        data['user'] = user
        return data

    def create(self, data):
        """Create token to identify the user and update the last login date"""
        user = data['user']
        delete_user_sessions(user)  # Delete users sessions
        update_last_login(None, user)  # Update the last login date
        refresh = self.get_token(user)  # Get tokens
        self.context['refresh'] = str(refresh)
        self.context['access'] = str(refresh.access_token)
        return user


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
                {'errors': 'El token es inválido o ha expirado'}, code='token_invalid'
            )


class VerifyTokenSerializer(serializers.Serializer):
    """Verify token serializer"""
    token = serializers.CharField()

    def validate_token(self, value):
        """Verify token is valid."""
        self.context['payload'] = verify_token(value)
        return value


class PasswordResetSerializer(serializers.Serializer):
    """
    Find user account serializer.
    Finds the user account given a user name and send email reset password.
    """

    username = serializers.CharField()

    def validate_username(self, value):
        """Verify that the user account exists"""
        user = User.objects.filter(username=value, is_active=True).first()
        if user is None:
            raise serializers.ValidationError(
                {'errors': 'El usuario no está asignado a ninguna cuenta.'}, code='account_not_found'
            )
        self.instance = user
        return value

    def save(self, **kwargs):
        """Send password reset email"""

        if self.instance.email is None:
            self.context['send_email'] = False
        else:
            send = self.send_password_reset_email(self.instance)
            self.context['send_email'] = send == 1

        return self.instance

    def send_password_reset_email(self, user):
        """Send reset password link to given user."""
        token = generate_token(user, 'password_reset')
        url = f'{settings.DEFAULT_DOMAIN}/password/reset/key/{token}'
        template_prefix = 'accounts/email/password_reset_key'
        context = {'user': user, 'password_reset_url': url}
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = " ".join(subject.splitlines()).strip()  # Remove superfluous line breaks
        content = render_to_string(f'{template_prefix}_message.html', context)
        msg = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(content, "text/html")
        return msg.send()


class PasswordResetFromKeySerializer(serializers.Serializer):
    """Password reset from key serializer"""

    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password2 = serializers.CharField(min_length=8)

    def validate_token(self, value):
        """Verify token is valid."""
        self.context['payload'] = verify_token(value)
        return value

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def save(self, **kwargs):
        """Update user´s password"""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'], is_active=True)
        user.set_password(self.validated_data['password2'])
        user.save(update_fields=['password', 'updated_at'])
