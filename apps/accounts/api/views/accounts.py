"""Account views"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts.api.serializers.accounts import (
    UserSignUpSerializer, UserLoginSerializer, PasswordResetSerializer, PasswordResetFromKeySerializer,
    VerifyTokenSerializer
)
from apps.accounts.api.serializers.users import UserListSerializer
from apps.accounts.utils import delete_user_sessions
from gestion_consultas.exceptions import BadRequest


class AccountsViewSet(GenericViewSet):
    """Accounts API view."""

    @action(methods=['post'], detail=False)
    def signup(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user, token = serializer.save()
            data = {
                'access_token': token,
                'user': UserListSerializer(user).data,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'access_token': token,
            'user': UserListSerializer(user).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def logout(self, request):
        token = request.data.get('token')
        if token:
            token = Token.objects.filter(key=token).first()
            if token:
                user = token.user
                # Delete users sessions
                delete_user_sessions(user, token)
                return Response({'success': True, 'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
            raise BadRequest('No se ha encontrado un usuario con estas credenciales')
        raise BadRequest('No se ha encontrado un token en la petición')

    @action(methods=['post'], detail=False, url_path='verify-token')
    def verify_token(self, request):
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'success': True,
            'payload': serializer.context['payload'],
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='password-reset')
    def password_reset(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'send_email': serializer.context['send_email'],
            'username': user.username,
            'email': user.email,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='password-reset-from-key')
    def password_reset_from_key(self, request):
        serializer = PasswordResetFromKeySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                'success': True,
                'message': 'Restablecimiento de contraseña completado',
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
