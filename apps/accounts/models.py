"""Accounts models"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator, RegexValidator, FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.permissions import create_permissions
from gestion_consultas.utils import REGEX_LETTERS_ONLY


class UserManager(BaseUserManager):
    """Custom User Manager"""

    def _create_user(
            self, role, first_name, last_name, identification_number, username, email, phone, password, **extra_fields
    ):
        """
        Create a user. This function is called from the console.
        :param extra_fields: fields defined in the User model.
        :return: User
        """
        user = self.model(
            role=role,
            first_name=first_name,
            last_name=last_name,
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
            self, role, first_name, last_name, identification_number, username, email, phone, password, **extra_fields
    ):
        """
        Create a user
        :return: User
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            role, first_name, last_name, identification_number, username, email, phone, password, **extra_fields
        )

    def create_superuser(
            self, first_name, last_name, identification_number, username, email, phone, password, **extra_fields
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
            'ADMIN', first_name, last_name, identification_number, username, email, phone, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""

    class Type(models.TextChoices):
        """User types"""

        ADMIN = 'ADMIN', _('Administrador')
        DOCTOR = 'DOC', _('Doctor')
        USER = 'USR', _('Usuario')

    class IdentificationType(models.TextChoices):
        CC = 'CC', _('Cédula de Ciudadanía')
        CE = 'CE', _('Cédula de Extranjería')
        NIT = 'NIT', _('Nit')

    role = models.CharField(_('tipo de usuario'), max_length=8, choices=Type.choices, default=Type.USER)
    first_name = models.CharField(_('nombre'), max_length=60, validators=[
        MinLengthValidator(limit_value=2, message=_('El nombre debe tener al menos 2 caracteres.')),
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('Su nombre debe tener solo letras (A-Z).'),
            code='invalid_first_name'
        ),
    ])
    last_name = models.CharField(_('apellidos'), max_length=60, validators=[
        MinLengthValidator(limit_value=2, message=_('Sus apellidos deben tener al menos 2 caracteres.')),
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('Sus apellidos deben tener solo letras (A-Z).'),
            code='invalid_last_name'
        ),
    ])
    identification_type = models.CharField(
        _('tipo de identificación'),
        max_length=3,
        choices=IdentificationType.choices,
        default=IdentificationType.CC
    )
    identification_number = models.CharField(
        _('número de identificación'),
        max_length=10,
        unique=True,
        null=True,
        blank=True,
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
        blank=True,
        null=True,
        error_messages={
            'unique': _('Ya existe un usuario con este correo electrónico.')
        }
    )
    phone = models.CharField(verbose_name=_('teléfono'), max_length=12, null=True, blank=True)
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
    neighborhood = models.CharField(_('barrio'), max_length=40, null=True, blank=True, validators=[
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('El nombre del barrio debe tener solo letras (A-Z).'),
            code='invalid_city'
        ),
    ])
    address = models.CharField(_('dirección'), max_length=60, null=True, blank=True)
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
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'identification_number', 'email', 'phone']

    class Meta:
        db_table = 'user'
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        permissions = [
            ('password_rest', 'Generate password reset link')
        ]

    def __str__(self):
        return self.first_name

    def full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f'{self.first_name} {self.last_name}'.strip()

    def tokens(self):
        """Return access and refresh JWT tokens."""
        return RefreshToken.for_user(self)

    full_name.short_description = _('Nombre completo')


@receiver(post_save, sender=User)
def create_user_permissions(sender, instance, created, **kwargs):
    if created:
        create_permissions(sender, instance)
