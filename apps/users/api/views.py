"""Users views"""

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import (
    UserListSerializer, UserListAdminSerializer, UserCreateSerializer, UserSignUpSerializer, UserLoginSerializer,
)
from apps.users.models import User, delete_user_sessions
from gestion_consultas.exceptions import BadRequest
from gestion_consultas.permissions import IsAdminOrDoctorUser
from gestion_consultas.utils import UserType


class SignUpAPI(APIView):
    """User sign up API view."""

    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user, token = serializer.save()
            data = {
                'access_token': token,
                'user': UserListSerializer(user).data,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(ObtainAuthToken):
    """User login API view."""

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user, token = serializer.save()
            data = {
                'access_token': token,
                'user': UserListSerializer(user).data,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        raise BadRequest('Usuario o contraseña incorrectos')


class LogoutAPI(APIView):
    """User logout API view."""

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        if token:
            token = Token.objects.filter(key=token).first()
            if token:
                user = token.user
                # Delete users sessions
                delete_user_sessions(user, token)
                return Response({'success': True, 'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
            raise BadRequest('No se ha encontrado un usuario con estas credenciales')
        raise BadRequest('No se ha encontrado un token en la petición')


class UserViewSet(viewsets.ModelViewSet):
    """
    User view set.

    Only ADMIN and DOCTOR users can interact with the URLS in this view.
    """

    serializer_class = UserListAdminSerializer
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
        if request.user.user_type == UserType.ADMIN:
            user_serializer = self.get_serializer(self.get_queryset(pk))
        else:
            user_serializer = UserListSerializer(self.get_queryset(pk))
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(self.get_queryset(), many=True)
        if request.user.user_type == UserType.DOCTOR:
            user_serializer = UserListSerializer(self.get_queryset(), many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Handle user create"""
        if request.user.user_type == UserType.ADMIN:
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response(UserListAdminSerializer(user).data, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied()
