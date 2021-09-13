"""Appointments filters"""

from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import FilterSet, CharFilter, MultipleChoiceFilter, OrderingFilter

from apps.appointments.models import Appointment


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
            'start_date', 'end_date', 'created_at', 'updated_at', 'doctor__username'
        ]

    order_by = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )

    @classmethod
    def filter_by_type(cls, queryset, name, value):
        return queryset.filter(type__contains=value[0])

    @classmethod
    def filter_by_full_name(cls, queryset, name, value):
        return (queryset.annotate(full_name=Concat('user__first_name', Value(' '), 'user__last_name')).
                filter(full_name__unaccent__icontains=value))
