"""Users views"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.api.permissions import IsAdminOrDoctorUser
from apps.users.api.serializers.users import (
    UserListSerializer, UserListAdminSerializer, UserCreateSerializer, UserPasswordChangeSerializer,
    UserProfileUpdateSerializer
)
from apps.users.models import User


class UserViewSet(viewsets.ModelViewSet):
    """
    User view set.

    Only ADMIN and DOCTOR users can interact with the URLS in this view.
    """

    serializer_class = UserListAdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminOrDoctorUser,)

    def get_queryset(self, pk=None):
        if self.request.user.role == User.Type.ADMIN:
            return User.objects.all() if pk is None else User.objects.filter(pk=pk).first()
        # DOCTOR User
        if pk is None:
            return User.objects.filter(is_active=True).defer(*UserListSerializer.Meta.exclude)
        return User.objects.filter(is_active=True, pk=pk).defer(*UserListSerializer.Meta.exclude).first()

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
        user_serializer = self.get_serializer(self.get_queryset(), many=True)
        if request.user.role == User.Type.DOCTOR:
            user_serializer = UserListSerializer(self.get_queryset(), many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Handle user create"""
        if request.user.role == User.Type.ADMIN:
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response(UserListAdminSerializer(user).data, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied()

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        """Logged user profile"""
        user = request.user
        if user.role == User.Type.ADMIN:
            user_serializer = self.get_serializer(self.get_queryset(user.id))
        else:
            user_serializer = UserListSerializer(self.get_queryset(user.id))
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='profile', url_name='profile',
            permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update user profile"""
        serializer = UserProfileUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='change-password', url_name='change_password',
            permission_classes=[IsAuthenticated], )
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
