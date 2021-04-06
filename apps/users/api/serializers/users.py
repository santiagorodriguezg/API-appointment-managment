"""Users serializers"""

from rest_framework import serializers

from apps.users.models import User, clean_password2


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
        if validated_data['role'] == User.Type.ADMIN:
            user.is_superuser = True
            user.is_staff = True
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User create serializer.
    An ADMIN user can update users of any type.
    """

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'created_at', 'updated_at')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    User profile serializer.
    A user can update your profile
    """

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'identification_type', 'identification_number', 'phone', 'email', 'city',
            'address', 'username',
        )


class UserPasswordChangeSerializer(serializers.Serializer):
    """User password change serializer."""

    password_old = serializers.CharField(min_length=8)
    password = serializers.CharField(min_length=8)
    password2 = serializers.CharField(min_length=8)

    def validate_password_old(self, value):
        """Validate that the old_password field is correct."""

        if not self.instance.check_password(value):
            raise serializers.ValidationError('Su contraseña actual es incorrecta', code='password_incorrect')
        return value

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def update(self, instance, validated_data):
        """Update user password"""
        self.instance.set_password(validated_data['password2'])
        self.instance.save(update_fields=['password', 'updated_at'])
        return self.instance
