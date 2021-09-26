"""User views"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.accounts.api.filters.users import UserFilter
from apps.accounts.api.permissions import IsAdminOrDoctorUser
from apps.accounts.api.serializers.users import (
    UserListSerializer, UserListAdminSerializer, UserCreateSerializer, UserPasswordChangeSerializer,
    UserProfileUpdateSerializer, UserUpdateSerializer, UserPasswordResetSerializer
)
from apps.accounts.models import User
from gestion_consultas.utils import UnaccentedSearchFilter


class UserModelViewSet(viewsets.ModelViewSet):
    """
    User view set.

    Only ADMIN and DOCTOR users can interact with the URLS in this view.
    """

    serializer_class = UserListAdminSerializer
    filter_backends = (DjangoFilterBackend, UnaccentedSearchFilter, OrderingFilter)
    filterset_class = UserFilter
    search_fields = ['~city', '~neighborhood', '~address']
    ordering = ('-created_at',)
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['destroy']:
            permission = [IsAdminUser]
        elif self.action in ['list', 'retrieve']:
            permission = [IsAdminOrDoctorUser]
        else:
            permission = [IsAuthenticated]
        return [p() for p in permission]

    def get_queryset(self, username=None):
        """Get the list of items for this view."""
        queryset = User.objects.all()
        if self.request.user.role == User.Type.ADMIN:
            return queryset if username is None else queryset.filter(username=username).first()
        # DOCTOR User
        if username is None:
            return queryset.filter(is_active=True).defer(*UserListSerializer.Meta.exclude)
        return queryset.filter(is_active=True, username=username).defer(*UserListSerializer.Meta.exclude).first()

    def retrieve(self, request, username=None, *args, **kwargs):
        """User by username"""
        qs = self.get_queryset(username)
        if qs is None:
            raise NotFound(detail='Usuario no encontrado.')

        if request.user.role == User.Type.ADMIN:
            serializer = self.get_serializer(qs)
        else:
            serializer = UserListSerializer(qs)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """User list"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        if request.user.role == User.Type.DOCTOR:
            serializer = UserListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Handle user create"""
        if not request.user.has_perm('accounts.add_user'):
            raise PermissionDenied()

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserListAdminSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username=None, *args, **kwargs):
        """Update users for given Id"""
        if not request.user.has_perm('accounts.change_user'):
            raise PermissionDenied()

        qs = self.get_queryset(username)
        if qs is None:
            raise NotFound(detail='Usuario no encontrado.')
        partial = request.method == 'PATCH'
        serializer = UserUpdateSerializer(qs, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get', 'put', 'patch'], detail=False)
    def me(self, request):
        """Get and update the logged-in user's profile"""
        user = request.user
        if request.method == 'GET':
            if user.role == User.Type.ADMIN:
                serializer = self.get_serializer(self.get_queryset(user.username))
            else:
                serializer = UserListSerializer(self.get_queryset(user.username))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            partial = request.method == 'PATCH'
            serializer = UserProfileUpdateSerializer(
                user, data=request.data, partial=partial, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=False, url_path='password/change')
    def change_password(self, request):
        """User change password"""
        serializer = UserPasswordChangeSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': True, 'message': 'Su contraseña fue actualizada correctamente.'},
                status=status.HTTP_201_CREATED
            )
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, url_path='password/reset')
    def password_reset(self, request, username=None):
        """User password reset link for given username"""
        if not request.user.has_perm('accounts.password_reset'):
            raise PermissionDenied()

        serializer = UserPasswordResetSerializer(data={'username': username})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'username': user.username,
            'full_name': user.get_full_name(),
            'password_reset_url': serializer.context['password_reset_url'],
        }
        return Response(data, status=status.HTTP_200_OK)
