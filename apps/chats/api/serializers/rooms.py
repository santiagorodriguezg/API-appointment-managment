"""Room serializer"""

from rest_framework import serializers

from apps.chats.models import Room, Message
from apps.accounts.api.serializers.users import UserListRelatedSerializer
from apps.chats.api.serializers.messages import LastMessageSerializer


class RoomSerializer(serializers.ModelSerializer):
    """Room serializer"""

    user_owner = UserListRelatedSerializer(read_only=True)
    user_receiver = UserListRelatedSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_last_message(self, obj):
        msg = Message.objects.filter(room=obj).order_by('created_at').last()
        return LastMessageSerializer(msg).data
