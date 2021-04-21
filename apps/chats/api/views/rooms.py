"""Room views"""

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.chats.models import Room
from apps.chats.api.serializers.rooms import RoomSerializer
from apps.accounts.api.permissions import check_permissions
from apps.accounts.api.views.users import UserModelViewSet
from gestion_consultas.utils import get_queryset_with_pk


class RoomListViewSet(ReadOnlyModelViewSet):
    """
    Room list view set
    """

    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('id',)

    def get_queryset(self, user=None, pk=None):
        """Get the list of items for this view."""
        detail = 'Chat no encontrado.'
        queryset = Room.objects.order_by('id').filter(Q(user_owner=user['id']) | Q(user_receiver=user['id']))
        return get_queryset_with_pk(detail, queryset, pk)

    def list(self, request, username=None, *args, **kwargs):
        """User list chat rooms"""
        check_permissions(request.user, username, 'chats.view_room')
        user_model_view_set = UserModelViewSet(request=request, format_kwarg=self.format_kwarg)
        user = user_model_view_set.retrieve(request, username, *args, **kwargs).data
        queryset = self.filter_queryset(self.get_queryset(user))
        page = self.paginate_queryset(queryset)

        rooms = self.get_serializer(page, many=True).data
        for room in rooms:
            if room['user_owner']['username'] == user['username']:
                room.pop('user_owner')

            if room['user_receiver']['username'] == user['username']:
                room.pop('user_receiver')

        data = {
            'user': user,
            'rooms': rooms
        }
        return self.get_paginated_response(data)

    def retrieve(self, request, username=None, pk=None, *args, **kwargs):
        """User chat room given Id"""
        check_permissions(request.user, username, 'chats.view_room')
        user_model_view_set = UserModelViewSet(request=request, format_kwarg=self.format_kwarg)
        user = user_model_view_set.retrieve(request, username, *args, **kwargs).data
        queryset = self.get_queryset(user, pk)

        room = self.get_serializer(queryset).data
        if room['user_owner']['username'] == user['username']:
            room.pop('user_owner')

        if room['user_receiver']['username'] == user['username']:
            room.pop('user_receiver')

        data = {
            'user': user,
            'room': room
        }
        return Response(data, status=status.HTTP_200_OK)
