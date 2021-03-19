"""Users serializers"""
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserListSerializer(serializers.ModelSerializer):
    """User List model serializer."""

    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_active', 'is_staff', 'groups', 'user_permissions')


class UserLoginSerializer(serializers.Serializer):
    """
    User login serializer.
    Handle the login request data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Check credentials"""

        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError({
                'errors': 'Correo electrónico o contraseña incorrectos'
            }, code='authorization')

        # if not user.is_verified:
        #     raise serializers.ValidationError('Account is not active yet :(')

        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        if not created:
            # Delete users sessions
            all_sessions = Session.objects.filter(expire_date__gte=datetime.now())
            if all_sessions.exists():
                for session in all_sessions:
                    session_data = session.get_decoded()
                    if self.context['user'].id == int(session_data.get('_auth_user_id')):
                        session.delete()
            # Update token
            token.delete()
            token = Token.objects.create(user=self.context['user'])

        return self.context['user'], token.key
