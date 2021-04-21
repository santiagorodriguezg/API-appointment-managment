"""Chats models"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    """Room model. Represents a chat room"""

    user_owner = models.ForeignKey(
        'accounts.User', verbose_name=_('usuario que crea el chat'), related_name='user_owner', on_delete=models.CASCADE
    )
    user_receiver = models.ForeignKey(
        'accounts.User', verbose_name=_('usuario con quien comparte el chat'), related_name='user_receiver',
        on_delete=models.CASCADE
    )
    name = models.CharField(_('nombre'), max_length=60, unique=True)
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)

    class Meta:
        db_table = 'room'
        verbose_name = _('chat')
        verbose_name_plural = _('chats')
        permissions = [
            ('add_room_from_me', 'Can add my rooms'),
            ('change_room_from_me', 'Can change my rooms'),
            ('delete_room_from_me', 'Can delete my rooms'),
            ('view_room_from_me', 'Can view my rooms'),
        ]

    def __str__(self):
        return f'{self.user_owner.username} | {self.user_receiver.username}'


class Message(models.Model):
    """Message model"""

    room = models.ForeignKey(Room, verbose_name=_('chat'), on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', verbose_name=_('usuario'), on_delete=models.CASCADE)
    content = models.TextField(_('contenido'))
    created_at = models.DateTimeField(_('fecha de registro'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        db_table = 'message'
        verbose_name = _('mensaje')
        verbose_name_plural = _('mensajes')
        permissions = [
            ('add_message_from_me', 'Can add my messages'),
            ('change_message_from_me', 'Can change my messages'),
            ('delete_message_from_me', 'Can delete my messages'),
            ('view_message_from_me', 'Can view my messages'),
        ]

    def __str__(self):
        return self.content
