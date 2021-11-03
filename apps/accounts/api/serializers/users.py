"""User serializers"""

from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.tasks import send_email_to_user_created_by_admin
from apps.accounts.utils import clean_password2, validate_username, generate_password_reset_link


class UserBaseModelSerializer(serializers.ModelSerializer):
    """User base model serializer add full_name field"""

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserListAdminSerializer(UserBaseModelSerializer):
    """
    User list ADMIN serializer.
    If the user has ADMIN permissions it lists all fields of the user model.
    """

    class Meta:
        model = User
        exclude = ('password',)


class UserListSerializer(UserBaseModelSerializer):
    """
    User list model serializer.
    Lists the fields of the user model to which the DOC user has permissions.
    """

    class Meta:
        model = User
        exclude = ('password', 'is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions')


class UserListRelatedSerializer(UserBaseModelSerializer):
    """
    User list related serializer
    Display the user's basic data. Must be used for relational fields.
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'full_name', 'username', 'identification_number', 'picture')


class UserListingField(serializers.RelatedField):
    """
    Used to define a relational field to serialize a user to a custom string representation, using its username.
    """

    def to_representation(self, value):
        return value.username


class UserCreateSerializer(UserBaseModelSerializer):
    """
    User create serializer.
    An ADMIN user can create users of any type.
    """

    password2 = serializers.CharField(min_length=8)

    class Meta:
        model = User
        exclude = (
            'is_superuser', 'is_staff', 'last_login', 'created_at', 'updated_at', 'groups', 'user_permissions'
        )

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
        # Send email
        if user.email:
            send_email_to_user_created_by_admin.delay(user.id, validated_data['password'])
        return user


class UserUpdateSerializer(UserBaseModelSerializer):
    """
    User update serializer.
    An ADMIN user can update users of any type.
    """

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'created_at', 'updated_at', 'groups', 'user_permissions')


class UserProfileUpdateSerializer(UserBaseModelSerializer):
    """
    User profile serializer.
    A user can update your profile
    """

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'identification_type', 'identification_number', 'phone', 'email', 'city',
            'neighborhood', 'address', 'username', 'picture'
        )


class UserPasswordChangeSerializer(serializers.Serializer):
    """User password change serializer."""

    password_old = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password2 = serializers.CharField(min_length=8)

    def validate_password_old(self, value):
        """Validate that the old_password field is correct."""

        if not self.instance.check_password(value):
            raise serializers.ValidationError('Su contraseña actual es incorrecta.', code='password_incorrect')
        return value

    def validate(self, data):
        """Verify passwords match"""
        return clean_password2(self.instance, data)

    def update(self, instance, validated_data):
        """Update user password"""
        self.instance.set_password(validated_data['password2'])
        self.instance.save(update_fields=['password', 'updated_at'])
        return self.instance


class UserPasswordResetSerializer(serializers.Serializer):
    """
    User password serializer.
    An ADMIN user can send a password reset link
    """

    username = serializers.CharField()

    def validate_username(self, value):
        """Verify that the user account exists"""
        self.instance = validate_username(value)
        return value

    def save(self, **kwargs):
        """Generate password reset link to given user."""
        self.context['password_reset_url'] = generate_password_reset_link(self.instance)
        return self.instance
