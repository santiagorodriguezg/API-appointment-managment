"""Room serializer"""

from rest_framework import serializers

from apps.accounts.api.serializers.users import UserListRelatedSerializer
from apps.chats.models import Room


class RoomSerializer(serializers.ModelSerializer):
    """Room serializer"""

    user_owner = UserListRelatedSerializer(read_only=True)
    user_receiver = UserListRelatedSerializer(read_only=True)

    class Meta:
        model = Room
        fields = '__all__'
