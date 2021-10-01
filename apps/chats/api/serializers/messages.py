"""Message serializer"""

from rest_framework import serializers

from apps.chats.models import Message
from apps.accounts.api.serializers.users import UserListingField


class MessageListSerializer(serializers.ModelSerializer):
    """Message list serializer"""

    user = UserListingField(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
