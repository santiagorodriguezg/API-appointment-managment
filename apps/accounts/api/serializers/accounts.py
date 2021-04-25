"""Account serializers"""

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.accounts.models import User
from apps.accounts.utils import clean_password2, delete_user_sessions, generate_token, verify_token


class UserSignUpSerializer(serializers.ModelSerializer):
    """
    User sign up serializer.
    Handle sign up data validation and user creation.
    """

    password2 = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'identification_type', 'identification_number', 'email', 'phone', 'city',
            'neighborhood', 'address', 'password', 'password2'
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
        # Create token
        token = Token.objects.create(user=user)
        return user, token.key


class UserLoginSerializer(serializers.Serializer):
    """
    User login serializer.
    Handle the login request data.
    """

    username = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=64)

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
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # Delete users sessions and generate new token
            delete_user_sessions(user, token)
            token = Token.objects.create(user=user)
        # Update the last login date
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return user, token.key


class VerifyTokenSerializer(serializers.Serializer):
    """Verify token serializer"""
    token = serializers.CharField()

    def validate_token(self, data):
        """Verify token is valid."""
        self.context['payload'] = verify_token(data)
        return data


class PasswordResetSerializer(serializers.Serializer):
    """
    Find user account serializer.
    Finds the user account given a user name and send email reset password.
    """

    username = serializers.CharField()

    def validate_username(self, data):
        """Verify that the user account exists"""
        user = User.objects.filter(username=data, is_active=True).first()
        if user is None:
            raise serializers.ValidationError(
                {'errors': 'El usuario no está asignado a ninguna cuenta.'}, code='account_not_found'
            )
        self.instance = user
        return data

    def save(self, **kwargs):
        """Send password reset email"""
        if self.instance.email is None:
            self.context['send_email'] = False
        else:
            self.send_password_reset_email(self.instance)
        return self.instance

    def send_password_reset_email(self, user):
        """Send reset password link to given user."""
        token = generate_token(user, 'password_reset')
        url = f'{settings.DEFAULT_DOMAIN}password/reset/key/{token}'
        template_prefix = 'users/email/password_reset_key'
        context = {'user': user, 'password_reset_url': url}
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = " ".join(subject.splitlines()).strip()  # Remove superfluous line breaks
        content = render_to_string(f'{template_prefix}_message.html', context)
        msg = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(content, "text/html")
        self.context['send_email'] = msg.send() == 1


class PasswordResetFromKeySerializer(serializers.Serializer):
    """Password reset from key serializer"""

    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password2 = serializers.CharField(min_length=8)

    def validate_token(self, data):
        """Verify token is valid."""
        self.context['payload'] = verify_token(data)
        return data

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def save(self, **kwargs):
        """Update user´s password"""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'], is_active=True)
        user.set_password(self.validated_data['password2'])
        user.save(update_fields=['password', 'updated_at'])
