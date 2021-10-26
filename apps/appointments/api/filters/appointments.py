"""Appointments filters"""

from django_filters import FilterSet, CharFilter, MultipleChoiceFilter, OrderingFilter

from apps.appointments.models import Appointment
from gestion_consultas.utils import filter_by_full_name


class AppointmentFilter(FilterSet):
    """Appointment filter"""

    type = MultipleChoiceFilter(
        field_name='type', choices=Appointment.APPOINTMENT_TYPE_CHOICES, method='filter_by_type'
    )
    user__username = CharFilter(field_name='user__username', lookup_expr='unaccent__icontains')
    user__identification_number = CharFilter(
        field_name='user__identification_number',
        lookup_expr='unaccent__icontains'
    )
    user__full_name = CharFilter(method='filter_by_full_name')

    class Meta:
        model = Appointment
        fields = [
            'id', 'start_date', 'end_date', 'created_at', 'updated_at', 'doctors__username'
        ]

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )

    @classmethod
    def filter_by_type(cls, queryset, name, value):
        return queryset.filter(type__contains=value[0])

    @classmethod
    def filter_by_full_name(cls, queryset, name, value):
        return filter_by_full_name(queryset, 'user__first_name', 'user__last_name', value)
