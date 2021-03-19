from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class Appointment(models.Model):
    """Appointment model. Represents a chat room"""

    patient = models.ForeignKey(User, verbose_name=_('paciente'), related_name='patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey(
        User, verbose_name=_('doctor'), related_name='doctor', on_delete=models.CASCADE, null=True, blank=True
    )
    start_time = models.DateTimeField(_('fecha de inicio'), null=True, blank=True)
    end_time = models.DateTimeField(_('fecha de finalización'), null=True, blank=True)
    description = models.TextField(_('descripción'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de modificación de la cuenta'), auto_now=True)

    class Meta:
        db_table = 'appointment'
        verbose_name = _('cita')
        verbose_name_plural = _('citas')

    def __str__(self):
        return self.description
