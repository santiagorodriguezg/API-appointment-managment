"""Users views"""
from rest_framework import status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from apps.users.api.serializers import UserLoginSerializer, UserListSerializer, UserSerializer
from apps.users.models import User
from gestion_consultas.permissions import IsAdminOrDoctorUser
from gestion_consultas.utils import UserType


class LoginAPI(ObtainAuthToken):
    """User login API view."""

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'access_token': token,
            'user': UserListSerializer(user).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    User view set.

    Only ADMIN and DOCTOR users can interact with the URLS in this view.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    permission_classes = (IsAdminOrDoctorUser,)

    def get_queryset(self, pk=None):
        if self.request.user.user_type == UserType.ADMIN:
            return User.objects.all() if pk is None else User.objects.filter(pk=pk).first()
        # DOCTOR User
        if pk is None:
            return User.objects.filter(is_active=True).defer(*UserListSerializer.Meta.exclude)
        return User.objects.filter(is_active=True, pk=pk).defer(*UserListSerializer.Meta.exclude).first()

    def retrieve(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            user_serializer = self.get_serializer(self.get_queryset(pk))
        else:
            user_serializer = UserListSerializer(self.get_queryset(pk))
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(self.get_queryset(), many=True)
        if request.user.user_type == UserType.DOCTOR:
            user_serializer = UserListSerializer(self.get_queryset(), many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
