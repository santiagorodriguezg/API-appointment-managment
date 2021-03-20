"""Users views"""
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

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


class LogoutAPI(APIView):
    """User logout API view."""

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        if token:
            token = Token.objects.filter(key=token).first()
            if token:
                user = token.user
                # Delete users sessions
                all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        session_user = session_data.get('_auth_user_id')
                        if session_user:
                            if user.id == int(session_user):
                                session.delete()
                token.delete()
                return Response({'success': True, 'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
            return Response(
                {'error': 'No se ha encontrado un usuario con estas credenciales'}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'error': 'No se ha encontrado un token en la petición'}, status=status.HTTP_409_CONFLICT
        )


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
