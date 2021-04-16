"""Chats models"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    """Room model. Represents a chat room"""

    user = models.ForeignKey('accounts.User', verbose_name=_('usuario'), on_delete=models.CASCADE)
    name = models.CharField(_('chat'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)

    class Meta:
        db_table = 'room'
        verbose_name = _('chat')
        verbose_name_plural = _('chats')

    def __str__(self):
        return self.name


class Message(models.Model):
    """Message model"""

    room = models.ForeignKey(Room, verbose_name=_('chat'), on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', verbose_name=_('usuario'), on_delete=models.CASCADE)
    content = models.TextField(_('contenido'))
    from_doctor = models.BooleanField(_('enviado por un doctor?'), default=False)
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)

    class Meta:
        db_table = 'message'
        verbose_name = _('mensaje')
        verbose_name_plural = _('mensajes')

    def __str__(self):
        return self.content
