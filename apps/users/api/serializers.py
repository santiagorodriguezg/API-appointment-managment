"""Users serializers"""
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from apps.users.models import User, delete_user_sessions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserListSerializer(serializers.ModelSerializer):
    """User List model serializer."""

    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_active', 'is_staff', 'groups', 'user_permissions')


class UserLoginSerializer(AuthTokenSerializer):
    """
    User login serializer. Handle the login request data.
    """

    def create(self, attrs):
        """Create token to identify the user and update the last login date"""
        user = attrs['user']
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # Delete users sessions and generate new token
            delete_user_sessions(user, token)
            token = Token.objects.create(user=user)
        # Update the last login date
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return user, token.key
