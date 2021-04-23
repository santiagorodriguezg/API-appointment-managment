"""Chats factory"""

import factory
from django.utils import timezone

from apps.chats.models import Room, Message
from tests.users.factories import UserFactory, UserAdminFactory


class RoomFactory(factory.django.DjangoModelFactory):
    """Room factory"""

    class Meta:
        model = Room

    user_owner = factory.SubFactory(UserAdminFactory)
    user_receiver = factory.SubFactory(UserFactory)
    name = factory.Faker('md5', raw_output=False)
    created_at = factory.LazyFunction(timezone.now)


class MessageFactory(factory.django.DjangoModelFactory):
    """Message factory"""

    class Meta:
        model = Message

    room = factory.SubFactory(RoomFactory)
    user = factory.SubFactory(UserAdminFactory)
    content = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


ROOM_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=RoomFactory)
MESSAGE_FACTORY_DICT = factory.build(dict, FACTORY_CLASS=MessageFactory)
