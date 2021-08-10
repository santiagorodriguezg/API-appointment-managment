"""Appointment views"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.accounts.api.permissions import check_permissions
from apps.accounts.api.views.users import UserModelViewSet
from apps.accounts.models import User
from apps.appointments.api.filters.appointments import AppointmentFilter
from apps.appointments.api.serializers.appointments import (
    AppointmentSerializer, AppointmentUserSerializer, AppointmentListSerializer
)
from apps.appointments.models import Appointment
from gestion_consultas.utils import UnaccentedSearchFilter, get_queryset_with_pk


class AppointmentListAPIView(ListAPIView):
    """
    Appointment List API View
    List all appointments of all users by ADMIN users only.
    """

    serializer_class = AppointmentListSerializer
    queryset = Appointment.objects.all()
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend, UnaccentedSearchFilter, OrderingFilter)
    search_fields = ['~user__city', '~user__neighborhood', '~user__address']
    filterset_class = AppointmentFilter
    ordering = ('id',)


class AppointmentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Appointment model view set"""

    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, UnaccentedSearchFilter, OrderingFilter)
    filterset_fields = ('start_date', 'end_date', 'created_at', 'updated_at', 'doctor__username')
    search_fields = ['~user__city', '~user__neighborhood', '~user__address']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ('id',)

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
        queryset = Appointment.objects.order_by('id').filter(user=user['id'])
        if user['role'] == User.Type.DOCTOR:
            queryset = Appointment.objects.order_by('id').filter(doctor=user['id'])
        return get_queryset_with_pk(detail, queryset, pk)

    def create(self, request, username=None, *args, **kwargs):
        """Users with ADMIN and USER roles can create appointments."""
        check_permissions(request.user, username, 'appointments.add_appointment')
        serializer = AppointmentUserSerializer(data=request.data, context={'request': request})
        if request.user.role == User.Type.ADMIN:
            user = User.objects.get(username=username)
            serializer = self.get_serializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, username=None, *args, **kwargs):
        """User appointments"""
        check_permissions(request.user, username, 'appointments.view_appointment')
        user_model_view_set = UserModelViewSet(request=request, format_kwarg=self.format_kwarg)
        user = user_model_view_set.retrieve(request, username, *args, **kwargs).data
        queryset = self.filter_queryset(self.get_queryset(user))
        page = self.paginate_queryset(queryset)
        data = {
            'user': user,
            'appointments': self.get_serializer(page, many=True).data
        }
        return self.get_paginated_response(data)

    def retrieve(self, request, username=None, pk=None, *args, **kwargs):
        """User appointments given Id"""
        check_permissions(request.user, username, 'appointments.view_appointment')
        user_model_view_set = UserModelViewSet(request=request, format_kwarg=self.format_kwarg)
        user = user_model_view_set.retrieve(request, username, *args, **kwargs).data
        queryset = self.get_queryset(user, pk)
        data = {
            'user': user,
            'appointment': self.get_serializer(queryset).data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, username=None, pk=None, *args, **kwargs):
        """Users with ADMIN and USER roles can update appointments."""
        check_permissions(request.user, username, 'appointments.change_appointment')
        user_model_view_set = UserModelViewSet(request=request, format_kwarg=self.format_kwarg)
        user = user_model_view_set.retrieve(request, username, *args, **kwargs).data
        queryset = self.get_queryset(user, pk)

        serializer = AppointmentUserSerializer(queryset, data=request.data, context={'request': request})
        if request.user.role == User.Type.ADMIN:
            serializer = self.get_serializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
