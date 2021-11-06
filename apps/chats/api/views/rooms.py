"""Room views"""

from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.accounts.api.permissions import check_permissions
from apps.accounts.api.views.users import UserModelViewSet
from apps.chats.api.serializers.rooms import RoomSerializer
from apps.chats.models import Room


class RoomListViewSet(ReadOnlyModelViewSet):
    """
    Room list view set
    """

    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'name'

    def get_user(self, request, username, *args, **kwargs):
        """Get user from UserModelViewSet class"""
        user_model_view_set = UserModelViewSet(
            request=request,
            format_kwarg=self.format_kwarg,
            kwargs={'username': username}
        )
        return user_model_view_set.retrieve(request, username, *args, **kwargs).data

    def get_queryset(self, user=None, pk=None):
        """Get the list of items for this view."""
        return Room.objects.order_by('-created_at').filter(Q(user_owner=user['id']) | Q(user_receiver=user['id']))

    def get_object(self, user=None, room_name=None):
        queryset = self.filter_queryset(self.get_queryset(user=user))
        queryset = queryset.filter(name=room_name).first()
        if queryset is None:
            raise NotFound(detail='Chat no encontrado.')
        return queryset

    def list(self, request, username=None, *args, **kwargs):
        """User list chat rooms"""
        check_permissions(request.user, username, 'chats.view_room')
        user = self.get_user(request, username, *args, **kwargs)
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

    def retrieve(self, request, username=None, name=None, *args, **kwargs):
        """User chat room given Id"""
        check_permissions(request.user, username, 'chats.view_room')
        user = self.get_user(request, username, *args, **kwargs)
        queryset = self.get_object(user, name)

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
