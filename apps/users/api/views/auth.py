"""Auth views"""
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers.auth import (
    UserSignUpSerializer, UserLoginSerializer, PasswordResetSerializer, PasswordResetFromKeySerializer,
    VerifyTokenSerializer
)
from apps.users.api.serializers.users import UserListSerializer
from apps.users.utils import delete_user_sessions
from gestion_consultas.exceptions import BadRequest


class SignUpAPIView(APIView):
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


class LoginAPIView(APIView):
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


class LogoutAPIView(APIView):
    """User logout API view."""

    def post(self, request, *args, **kwargs):
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


class VerifyTokenAPIView(APIView):
    """Verify token API view."""

    def post(self, request, *args, **kwargs):
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'success': True,
            'payload': serializer.context['payload'],
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    """Password reset API View"""

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'send_email': serializer.context['send_email'],
            'username': user.username,
            'email': user.email,
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetFromKeyAPIView(APIView):
    """Password reset from key API view."""

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetFromKeySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                'success': True,
                'message': 'Restablecimiento de contraseña completado',
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
