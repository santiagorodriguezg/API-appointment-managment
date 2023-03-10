"""Appointments models"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    """Appointment model. Represents a chat room"""

    APPOINTMENT_TYPE_CHOICES = [
        ('PSY', _('Psicosocial')),
        ('LEG', _('Jurídica')),
    ]

    user = models.ForeignKey('accounts.User', verbose_name=_('user'), related_name='patient', on_delete=models.CASCADE)
    doctors = models.ManyToManyField('accounts.User', verbose_name=_('doctores'), related_name='doctors', blank=True)
    type = models.CharField(verbose_name=_('tipo de cita'), max_length=7)
    children = models.JSONField(verbose_name=_('datos de los hijos'), null=True, blank=True)
    aggressor = models.JSONField(verbose_name=_('datos del agresor'), null=True, blank=True)
    description = models.TextField(_('descripción'), null=True, blank=True)
    audio = models.FileField(_('audio'), upload_to='appointments/audio', validators=[
        FileExtensionValidator(allowed_extensions=['mp3', 'mp4', 'ogg', 'm4a'])
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


class AppointmentMultimedia(models.Model):
    """Appointment Multimedia model"""

    class FileType(models.TextChoices):
        PDF = 'PDF', _('Archivo PDF')
        IMAGE = 'IMG', _('Imagen')
        VIDEO = 'VIDEO', _('Video')

    appointment = models.ForeignKey(
        Appointment, verbose_name=_('cita'), related_name='multimedia', on_delete=models.CASCADE
    )
    file = models.FileField(_('archivo'), upload_to='appointments/files', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'pdf'])
    ])
    file_type = models.CharField(_('tipo de archivo'), max_length=8, choices=FileType.choices)

    class Meta:
        db_table = 'appointment_multimedia'
        verbose_name = _('archivo de la cita')
        verbose_name_plural = _('archivos de las citas')

    def __str__(self):
        return self.file.name
