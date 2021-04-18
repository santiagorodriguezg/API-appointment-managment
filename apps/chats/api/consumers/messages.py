"""Message consumer"""

from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.permissions import IsAuthenticated
from djangochannelsrestframework.mixins import (
    ListModelMixin, CreateModelMixin, PatchModelMixin, DeleteModelMixin, RetrieveModelMixin
)

from apps.chats.models import Message
from apps.chats.api.serializers.messages import MessageSerializer


class MessageConsumer(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    PatchModelMixin,
    DeleteModelMixin,
    GenericAsyncAPIConsumer
):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
