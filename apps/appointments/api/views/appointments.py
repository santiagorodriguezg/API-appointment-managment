"""Appointment views"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.accounts.api.permissions import check_permissions
from apps.accounts.api.views.users import UserModelViewSet
from apps.appointments.api.filters.appointments import AppointmentFilter
from apps.appointments.api.serializers.appointments import (
    AppointmentSerializer, AppointmentUserSerializer, AppointmentListSerializer
)
from gestion_consultas.utils import UnaccentedSearchFilter, get_queryset_with_pk


class AppointmentListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Appointment List ViewSet
    List all appointments of all users by ADMIN users only.
    """

    serializer_class = AppointmentListSerializer
    queryset = Appointment.objects.all()
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend, UnaccentedSearchFilter, OrderingFilter)
    filterset_class = AppointmentFilter
    search_fields = ['~user__city', '~user__neighborhood', '~user__address']
    ordering = ('-created_at',)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('doctors', 'multimedia')


class AppointmentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Appointment model view set"""

    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, UnaccentedSearchFilter, OrderingFilter)
    filterset_class = AppointmentFilter
    ordering = ('-created_at',)

    def get_user(self, request, username):
        """Get user from UserModelViewSet class"""
        user_model_view_set = UserModelViewSet(
            request=request,
            format_kwarg=self.format_kwarg,
            kwargs={'username': username}
        )
        return user_model_view_set.get_object()

    def get_serializer_class(self):
        """Assign serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            serializer = AppointmentSerializer
        else:
            serializer = AppointmentListSerializer
        return serializer

    def get_queryset(self, user=None, pk=None):
        """Get the list of items for this view."""
        detail = 'Cita no encontrada.'
        queryset = Appointment.objects.order_by('id').filter(user=user).prefetch_related('doctors', 'multimedia')

        if user.role == User.Type.DOCTOR:
            queryset = Appointment.objects.filter(doctors=user).order_by('id')

        return get_queryset_with_pk(detail, queryset, pk)

    def create(self, request, username=None, *args, **kwargs):
        """Users with ADMIN and USER roles can create appointments."""
        check_permissions(request.user, username, 'appointments.add_appointment')
        serializer = AppointmentUserSerializer(data=request.data, context={'request': request})
        if request.user.role == User.Type.ADMIN:
            user = self.get_user(request, username)
            serializer = self.get_serializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, username=None, *args, **kwargs):
        """User appointments"""
        check_permissions(request.user, username, 'appointments.view_appointment')
        user = self.get_user(request, username)
        queryset = self.filter_queryset(self.get_queryset(user))
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    def retrieve(self, request, username=None, pk=None, *args, **kwargs):
        """User appointments given Id"""
        check_permissions(request.user, username, 'appointments.view_appointment')
        user = self.get_user(request, username)
        queryset = self.get_queryset(user, pk)
        return Response(self.get_serializer(queryset).data, status=status.HTTP_200_OK)

    def update(self, request, username=None, pk=None, *args, **kwargs):
        """Users with ADMIN and USER roles can update appointments."""
        check_permissions(request.user, username, 'appointments.change_appointment')
        user = self.get_user(request, username)
        queryset = self.get_queryset(user, pk)

        partial = request.method == 'PATCH'
        serializer = AppointmentUserSerializer(
            queryset, data=request.data, partial=partial, context={'request': request}
        )
        if request.user.role == User.Type.ADMIN:
            serializer = self.get_serializer(queryset, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
