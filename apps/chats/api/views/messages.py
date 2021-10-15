from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.chats.models import Message
from apps.accounts.api.permissions import check_permissions
from apps.chats.api.serializers.messages import MessageListSerializer
from apps.chats.api.views.rooms import RoomListViewSet


class MessageListViewSet(ListModelMixin, GenericViewSet):
    """
    Message list view set
    """

    serializer_class = MessageListSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('created_at',)

    def get_queryset(self, room_name=None):
        """Get the list of items for this view."""
        return Message.objects.filter(room__name=room_name).order_by('created_at')

    def list(self, request, username=None, name=None, *args, **kwargs):
        """List room messages"""
        check_permissions(request.user, username, 'chats.view_message')
        room_list_view_set = RoomListViewSet(request=request, format_kwarg=self.format_kwarg)
        data = room_list_view_set.retrieve(request, username, name, *args, **kwargs).data
        queryset = self.get_queryset(name)
        data['room']['messages'] = self.get_serializer(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)
