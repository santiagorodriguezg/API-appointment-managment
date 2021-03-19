from django.db import models
from django.utils.translation import gettext as _

REGEX_LETTERS_ONLY = '^[a-zA-ZÁ-ÿ+ ?]*$'


class UserType(models.TextChoices):
    """Contact types"""

    ADMIN = 'ADMIN', _('Administrador')
    DOCTOR = 'DOC', _('Doctor')
    USER = 'USR', _('Usuario')
