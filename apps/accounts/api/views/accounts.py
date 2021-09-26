"""Accounts views"""

from rest_framework import status, generics
from rest_framework.response import Response

from apps.accounts.api.serializers.accounts import (
    SignupSerializer, LoginSerializer, LogoutSerializer, PasswordResetEmailSerializer, PasswordResetCompleteSerializer
)
from apps.accounts.api.serializers.users import UserListSerializer
from apps.accounts.utils import get_user_from_uidb64, password_reset_check_token


class SignupAPIView(generics.GenericAPIView):
    """User sign up view"""

    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = {
                'access': serializer.context['access'],
                'refresh': serializer.context['refresh'],
                'user': UserListSerializer(user).data,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    """User sign in view"""

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'access': serializer.context['access'],
            'refresh': serializer.context['refresh'],
            'user': UserListSerializer(serializer.instance, context={'request': request}).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutAPIView(generics.GenericAPIView):
    """User logout view"""
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Logout exitoso.'}, status=status.HTTP_200_OK)


class PasswordResetEmailAPIView(generics.GenericAPIView):
    """Send password reset email"""

    serializer_class = PasswordResetEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'send_email': serializer.context['send_email'],
            'username': user.username,
            'email': user.email,
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(generics.GenericAPIView):
    """Verify that the token to reset the user's password is valid"""

    serializer_class = PasswordResetCompleteSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        user = get_user_from_uidb64(uidb64)
        password_reset_check_token(user, token)
        data = {
            'success': True,
            'message': 'El token es valido.'
        }
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetCompleteAPIView(generics.GenericAPIView):
    """Reset the user's password"""

    serializer_class = PasswordResetCompleteSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'success': True,
            'message': 'Restablecimiento de contraseña completado.',
        }
        return Response(data, status=status.HTTP_200_OK)
