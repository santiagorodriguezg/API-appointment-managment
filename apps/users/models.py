from django.contrib.auth import password_validation
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator, FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from gestion_consultas.utils import REGEX_LETTERS_ONLY, UserType


class UserManager(BaseUserManager):
    """Custom User Manager"""

    def _create_user(
            self, user_type, first_name, last_name, identification_type, identification_number, username, phone,
            password, email, **extra_fields
    ):
        """
        Create a user. This function is called from the console.
        :param extra_fields: fields defined in the User model.
        :return: User
        """
        user = self.model(
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            identification_type=identification_type,
            identification_number=identification_number,
            username=self.model.normalize_username(username),
            email=self.normalize_email(email),
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(
            self, user_type, first_name, last_name, identification_type, identification_number, username,
            phone, password, email=None, **extra_fields
    ):
        """
        Create a user
        :return: User
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            user_type, first_name, last_name, identification_type, identification_number, username, phone,
            password, email, **extra_fields
        )

    def create_superuser(
            self, first_name, last_name, identification_type, identification_number, username, phone, password,
            email=None, **extra_fields
    ):
        """
        Create user with administrator permissions
        :return: User
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            'ADMIN', first_name, last_name, identification_type, identification_number, username, phone, password,
            email, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""

    class IdentificationType(models.TextChoices):
        CC = 'CC', _('Cédula de Ciudadanía')
        CE = 'CE', _('Cédula de Extranjería')

    user_type = models.CharField(_('tipo de usuario'), max_length=8, choices=UserType.choices)
    first_name = models.CharField(_('nombre'), max_length=60, validators=[
        MinLengthValidator(limit_value=2, message=_('El nombre debe tener al menos 2 caracteres.')),
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('El nombre debe tener solo letras (A-Z).'),
            code='invalid_first_name'
        ),
    ])
    last_name = models.CharField(_('apellidos'), max_length=60, null=True, blank=True, validators=[
        MinLengthValidator(limit_value=2, message=_('Sus apellidos deben tener al menos 2 caracteres.')),
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('Sus apellidos deben tener solo letras (A-Z).'),
            code='invalid_last_name'
        ),
    ])
    identification_type = models.CharField(
        _('tipo de identificación'),
        max_length=2,
        choices=IdentificationType.choices,
        default=IdentificationType.CC
    )
    identification_number = models.CharField(
        _('número de identificación'),
        max_length=10,
        unique=True,
        error_messages={
            'unique': _('Ya existe un usuario con este número de identificación.')
        },
        validators=[
            MinLengthValidator(limit_value=6, message=_('Su identificación debe tener al menos 6 caracteres.')),
        ]
    )
    username = models.CharField(
        _('usuario'),
        max_length=60,
        unique=True,
        help_text=_('Su usuario debe tener máximo 60 caracteres. Letras, dígitos y @/./+/-/_ solamente.'),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': _('Ya existe un usuario con este nombre de usuario.'),
        },
    )
    email = models.EmailField(
        _('correo electrónico'),
        max_length=60,
        unique=True,
        null=True,
        blank=True,
        error_messages={
            'unique': _('Ya existe un contacto con este correo electrónico.')
        }
    )
    phone = models.CharField(verbose_name=_('teléfono'), max_length=12)
    picture = models.ImageField(_('foto de perfil'), upload_to='users/pictures', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
    ])
    city = models.CharField(_('ciudad'), max_length=60, null=True, blank=True, validators=[
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('El nombre de la ciudad debe tener solo letras (A-Z).'),
            code='invalid_city'
        ),
    ])
    address = models.CharField(_('dirección'), max_length=100, null=True, blank=True)
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Indica que la cuenta del usuario está activa.')
    )
    is_staff = models.BooleanField(
        _('login en admin'),
        default=False,
        help_text=_('Designa si este usuario puede acceder al sitio de administración.')
    )
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de modificación de la cuenta'), auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'identification_type', 'identification_number', 'phone', 'email']

    class Meta:
        db_table = 'user'
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')

    def __str__(self):
        return self.first_name

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    get_full_name.short_description = _('Nombre completo')


def delete_user_sessions(user, token):
    """Delete the authentication token and user sessions."""

    all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    if all_sessions.exists():
        for session in all_sessions:
            session_data = session.get_decoded()
            session_user = session_data.get('_auth_user_id')
            if session_user:
                if user.id == int(session_user):
                    session.delete()
    token.delete()


def clean_password2(instance, data):
    """Verify passwords match"""

    password1 = data.get("password")
    password2 = data.get("password2")
    if password1 and password2 and password1 != password2:
        raise serializers.ValidationError(
            {'password2': 'Las contraseñas ingresadas no coinciden'}, code='password_mismatch',
        )

    try:
        password_validation.validate_password(password2, instance)
    except ValidationError as error:
        raise serializers.ValidationError({'password2': error.messages}, code='password2')

    return data
