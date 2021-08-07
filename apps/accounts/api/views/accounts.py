"""Account views"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts.api.serializers.accounts import (
    SignUpSerializer, LoginSerializer, PasswordResetSerializer, PasswordResetFromKeySerializer,
    VerifyTokenSerializer, LogoutSerializer
)
from apps.accounts.api.serializers.users import UserListSerializer


class AccountsViewSet(GenericViewSet):
    """Accounts API view."""

    @action(methods=['post'], detail=False)
    def signup(self, request):
        """User sign up"""
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = {
                'access': serializer.context['access'],
                'refresh': serializer.context['refresh'],
                'user': UserListSerializer(user).data,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def login(self, request):
        """User sign in"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'access': serializer.context['access'],
            'refresh': serializer.context['refresh'],
            'user': UserListSerializer(user).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def logout(self, request):
        """User logout"""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Logout exitoso'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='token/verify')
    def verify_token(self, request):
        """Verify JWT token used to reset password"""
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'success': True,
            'payload': serializer.context['payload'],
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='password/reset')
    def password_reset(self, request):
        """Send password reset email"""
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
        """Verify JWT token and reset password"""
        serializer = PasswordResetFromKeySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                'success': True,
                'message': 'Restablecimiento de contraseña completado',
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
