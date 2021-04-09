"""Users serializers"""

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.users.models import User
from apps.users.utils import clean_password2, delete_user_sessions


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
        """Create token to identify the user and update the last login date"""

        user = self.context['user']
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # Delete users sessions and generate new token
            delete_user_sessions(user, token)
            token = Token.objects.create(user=user)
        # Update the last login date
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return user, token.key


# begin_password_reset
class FindUserAccountSerializer(serializers.Serializer):
    """
    Find user account serializer.
    Finds the user account given a user name.
    """

    username = serializers.CharField(min_length=8)

    def validate(self, data):
        """Verify that the user account exists"""

        user = User.objects.filter(username=data.get('username'), is_active=True).first()
        if user is None:
            raise serializers.ValidationError(
                {'errors': 'No se encontró su cuenta. Vuelva a intentarlo con otro usuario.'}, code='account_not_found'
            )
        self.context['user'] = user
        return data
