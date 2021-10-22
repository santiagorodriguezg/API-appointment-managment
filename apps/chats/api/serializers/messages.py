"""Message serializer"""

from rest_framework import serializers

from apps.chats.models import Message
from apps.accounts.api.serializers.users import UserListingField


class MessageListSerializer(serializers.ModelSerializer):
    """Message list serializer"""

    user = UserListingField(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'user', 'type', 'content', 'created_at', 'updated_at')


class LastMessageSerializer(serializers.ModelSerializer):
    """Serializes the last message sent in the chat room"""

    class Meta:
        model = Message
        fields = ('type', 'content', 'created_at', 'updated_at')
