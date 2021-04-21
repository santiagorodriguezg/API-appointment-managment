"""Message serializer"""

from rest_framework import serializers

from apps.accounts.api.serializers.users import UserListingField
from apps.accounts.models import User
from apps.chats.models import Room, Message


# class MessageSerializer(serializers.ModelSerializer):
#     """Room serializer"""
#
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#
#     class Meta:
#         model = Message
#         fields = ('user_receiver', 'content')
#
#     def create(self, validated_data):
#         room = Room.objects.create(
#             user_owner=self.context['user'],
#             user_receiver=validated_data['user_receiver']
#         )
#         msg = Message.objects.create(**validated_data, room=room, user=self.context['user'])
#         return msg


class MessageSerializer(serializers.Serializer):
    """Room serializer"""

    user_receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    content = serializers.CharField()

    def create(self, validated_data):
        user = self.context.get('scope').get('user')
        print("JAJAJ", user)
        room, created = Room.objects.get_or_create(
            user_owner=user,
            user_receiver=validated_data['user_receiver']
        )
        validated_data.pop('user_receiver')
        print("VALIDATE", validated_data)
        msg = Message(room=room, user=user, content=validated_data['content'])
        msg.save()
        return msg


class MessageListSerializer(serializers.ModelSerializer):
    """Message list serializer"""

    user = UserListingField(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
