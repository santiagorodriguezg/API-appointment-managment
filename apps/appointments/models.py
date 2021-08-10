"""Appointments models"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField


class Appointment(models.Model):
    """Appointment model. Represents a chat room"""

    APPOINTMENT_TYPE_CHOICES = [
        ('PSY', _('Psicológica')),
        ('JUD', _('Judicial')),
    ]

    user = models.ForeignKey('accounts.User', verbose_name=_('user'), related_name='patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey(
        'accounts.User', verbose_name=_('doctor'), related_name='doctor', on_delete=models.CASCADE, null=True,
        blank=True
    )
    type = MultiSelectField(verbose_name=_('tipo'), choices=APPOINTMENT_TYPE_CHOICES, min_choices=1)
    children = models.JSONField(verbose_name=_('hijos'), null=True, blank=True)
    aggressor = models.CharField(_('datos del posible agresor'), max_length=500, null=True, blank=True)
    description = models.TextField(_('descripción'), null=True, blank=True)
    audio = models.FileField(_('audio'), upload_to='appointments/audio', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['mp3', 'mp4'])
    ])
    start_date = models.DateTimeField(_('fecha de inicio'), null=True, blank=True)
    end_date = models.DateTimeField(_('fecha de finalización'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        db_table = 'appointment'
        verbose_name = _('cita')
        verbose_name_plural = _('citas')

        permissions = [
            ('add_appointment_from_me', 'Can add my appointments'),
            ('change_appointment_from_me', 'Can change my appointments'),
            ('delete_appointment_from_me', 'Can delete my appointments'),
            ('view_appointment_from_me', 'Can view my appointments'),
        ]

    def __str__(self):
        return self.description if self.description else ''
