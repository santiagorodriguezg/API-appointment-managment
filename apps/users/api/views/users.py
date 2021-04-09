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
    UserProfileUpdateSerializer, UserUpdateSerializer
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

    def get_queryset(self, pk=None):
        queryset = User.objects.all()
        if self.request.user.role == User.Type.ADMIN:
            return queryset if pk is None else queryset.filter(pk=pk).first()
        # DOCTOR User
        if pk is None:
            return queryset.filter(is_active=True).defer(*UserListSerializer.Meta.exclude)
        return queryset.filter(is_active=True, pk=pk).defer(*UserListSerializer.Meta.exclude).first()

    def retrieve(self, request, pk=None, *args, **kwargs):
        """User by pk"""
        qs = self.get_queryset(pk)
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

    def update(self, request, pk=None, *args, **kwargs):
        """Update users for given Id"""
        if request.user.role == User.Type.ADMIN:
            qs = self.get_queryset(pk)
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
                user_serializer = self.get_serializer(self.get_queryset(user.id))
            else:
                user_serializer = UserListSerializer(self.get_queryset(user.id))
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            partial = request.method == 'PATCH'
            serializer = UserProfileUpdateSerializer(user, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=False, url_path='change-password', url_name='change_password',
            permission_classes=[IsAuthenticated])
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
