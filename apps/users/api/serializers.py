"""Users serializers"""

from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from apps.users.models import User, delete_user_sessions, clean_password2
from gestion_consultas.utils import UserType


class UserListAdminSerializer(serializers.ModelSerializer):
    """
    User list ADMIN serializer.
    If the user has ADMIN permissions it lists all fields of the user model.
    """

    class Meta:
        model = User
        exclude = ('password',)


class UserListSerializer(serializers.ModelSerializer):
    """
    User List model serializer.
    Lists the fields of the user model to which the DOC user has permissions.
    """

    class Meta:
        model = User
        exclude = ('password', 'is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    User create serializer.
    An ADMIN user can create users of any type.
    """

    password2 = serializers.CharField(min_length=8)

    class Meta:
        model = User
        exclude = ('is_superuser', 'is_staff', 'last_login', 'created_at', 'updated_at')

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def create(self, validated_data):
        """Handle user creation"""

        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        if validated_data['user_type'] == UserType.ADMIN:
            user.is_superuser = True
            user.is_staff = True
        user.save()
        return user


class UserSignUpSerializer(serializers.ModelSerializer):
    """
    User sign up serializer.
    Handle sign up data validation and user creation.
    """

    password2 = serializers.CharField(min_length=8)

    class Meta:
        model = User
        exclude = ('user_type', 'is_active', 'is_superuser', 'is_staff', 'last_login', 'created_at', 'updated_at')

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def create(self, validated_data):
        """Handle user and token creation"""

        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.user_type = UserType.USER
        user.last_login = timezone.now()
        user.save()
        # Create token
        token = Token.objects.create(user=user)
        return user, token.key


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
