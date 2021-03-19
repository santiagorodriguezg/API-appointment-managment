from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinLengthValidator, RegexValidator, FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from gestion_consultas.utils import REGEX_LETTERS_ONLY, UserType


class UserManager(BaseUserManager):
    """Custom User Manager"""

    def _create_user(
            self, user_type, first_name, email, phone, password, is_staff, is_superuser, **extra_fields
    ):
        """
        Create a user. This function is called from the console.
        :param extra_fields: Extra fields that are defined in the REQUIRED_FIELDS constant.
        :return: User
        """
        user = self.model(
            user_type=user_type,
            first_name=first_name,
            email=self.normalize_email(email),
            phone=phone,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, user_type, first_name, email, phone, password, **extra_fields):
        """
        Create a user
        :return: User
        """
        return self._create_user(user_type, first_name, email, phone, password, False, False, **extra_fields)

    def create_superuser(self, first_name, email, phone, password, **extra_fields):
        """
        Create user with administrator permissions
        :return: User
        """
        return self._create_user('ADMIN', first_name, email, phone, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""

    class IdentificationType(models.TextChoices):
        CC = 'CC', _('Cédula de Ciudadanía')
        CE = 'CE', _('Cédula de Extranjería')

    user_type = models.CharField(_('tipo de usuario'), max_length=8, choices=UserType.choices)
    first_name = models.CharField(_('nombre'), max_length=60, validators=[
        MinLengthValidator(limit_value=3, message=_('El nombre debe tener al menos 3 caracteres.')),
        RegexValidator(
            regex=REGEX_LETTERS_ONLY,
            message=_('El nombre debe tener solo letras (A-Z).'),
            code='invalid_first_name'
        ),
    ])
    last_name = models.CharField(_('apellidos'), max_length=60, null=True, blank=True, validators=[
        MinLengthValidator(limit_value=3, message=_('Sus apellidos deben tener al menos 3 caracteres.')),
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
        default=IdentificationType.CC,
        null=True,
        blank=True
    )
    identification_number = models.CharField(
        _('número de identificación'),
        max_length=10,
        unique=True,
        error_messages={
            'unique': _('Ya existe un contacto con este número de identificación.')
        },
        null=True,
        blank=True,
        validators=[
            MinLengthValidator(limit_value=6, message=_('Su identificación debe tener al menos 6 caracteres.')),
        ]
    )
    email = models.EmailField(
        _('correo electrónico'),
        max_length=60,
        unique=True,
        error_messages={
            'unique': _('Ya existe un contacto con este correo electrónico.')
        }
    )
    phone = models.CharField(verbose_name=_('teléfono'), max_length=12)
    picture = models.ImageField(_('foto de perfil'), upload_to='users/pictures', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
    ])
    city = models.CharField(_('ciudad'), max_length=60, null=True, blank=True)
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
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

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
