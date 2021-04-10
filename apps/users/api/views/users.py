"""Users views"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.api.permissions import IsAdminOrDoctorUser
from apps.users.api.serializers.users import (
    UserListSerializer, UserListAdminSerializer, UserCreateSerializer, UserPasswordChangeSerializer,
    UserProfileUpdateSerializer, UserUpdateSerializer, UserPasswordResetSerializer
)
from apps.users.models import User
from gestion_consultas.utils import UnaccentedSearchFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    User view set.

    Only ADMIN and DOCTOR users can interact with the URLS in this view.
    """

    serializer_class = UserListAdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminOrDoctorUser,)
    filter_backends = (DjangoFilterBackend, UnaccentedSearchFilter, OrderingFilter)
    filterset_fields = ('identification_type', 'identification_number', 'role', 'is_active', 'is_superuser')
    search_fields = ['~first_name', '~last_name', '~city', '~neighborhood', '~address']
    ordering_fields = ['first_name', 'last_name', 'created_at', 'updated_at']
    ordering = ('id',)
    lookup_field = 'username'

    def get_queryset(self, username=None):
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
            user_serializer = self.get_serializer(qs)
        else:
            user_serializer = UserListSerializer(qs)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

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
        if request.user.role == User.Type.ADMIN:
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response(UserListAdminSerializer(user).data, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied()

    def update(self, request, username=None, *args, **kwargs):
        """Update users for given Id"""
        if request.user.role == User.Type.ADMIN:
            qs = self.get_queryset(username)
            if qs is None:
                raise NotFound(detail='Usuario no encontrado.')
            serializer = UserUpdateSerializer(qs, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied()

    @action(methods=['get', 'put', 'patch'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get and update the logged-in user's profile"""
        user = request.user
        if request.method == 'GET':
            if user.role == User.Type.ADMIN:
                user_serializer = self.get_serializer(self.get_queryset(user.username))
            else:
                user_serializer = UserListSerializer(self.get_queryset(user.username))
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            partial = request.method == 'PATCH'
            serializer = UserProfileUpdateSerializer(user, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=False, url_path='change-password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """User change password"""
        serializer = UserPasswordChangeSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success': True, 'message': 'Su contraseña fue actualizada correctamente'},
                status=status.HTTP_201_CREATED
            )
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, url_path='password-reset')
    def password_reset(self, request, username=None):
        """User password reset link for given username"""
        if request.user.role == User.Type.ADMIN:
            serializer = UserPasswordResetSerializer(data={'username': username})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {
                'success': True,
                'password_reset_url': serializer.context['password_reset_url'],
            }
            return Response(data, status=status.HTTP_200_OK)
        raise PermissionDenied()
