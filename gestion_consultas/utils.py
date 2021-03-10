from django.db import models
from django.utils.translation import gettext as _

REGEX_LETTERS_ONLY = '^[a-zA-ZÁ-ÿ+ ?]*$'


class UserType(models.TextChoices):
    """Contact types"""

    ADMIN = 'ADMIN', _('Administrador')
    WORKER = 'WKR', _('Trabajador')
    CUSTOMER = 'CUST', _('Cliente')
