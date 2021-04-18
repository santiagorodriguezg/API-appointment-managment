"""Message serializer"""

from rest_framework import serializers

from apps.accounts.api.serializers.users import UserListingField
from apps.accounts.models import User
from apps.chats.models import Room, Message


class MessageSerializer(serializers.ModelSerializer):
    """Room serializer"""

    user_receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ('content',)

    def create(self, validated_data):
        room = Room.objects.create(
            user_owner=self.context['user'],
            user_receiver=validated_data['user_receiver']
        )
        msg = Message.objects.create(**validated_data, room=room, user=self.context['user'])
        return msg


class MessageListSerializer(serializers.ModelSerializer):
    """Message list serializer"""

    user = UserListingField(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
