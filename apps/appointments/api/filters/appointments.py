"""Appointments filters"""

from django_filters import FilterSet, MultipleChoiceFilter, OrderingFilter

from apps.appointments.models import Appointment


class AppointmentFilter(FilterSet):
    """Appointment filter"""

    type = MultipleChoiceFilter(
        field_name='type', choices=Appointment.APPOINTMENT_TYPE_CHOICES, method='filter_by_type'
    )

    class Meta:
        model = Appointment
        fields = ['start_date', 'end_date', 'created_at', 'updated_at', 'user__username', 'doctor__username']

    order_by = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )

    @classmethod
    def filter_by_type(cls, queryset, name, value):
        return queryset.filter(type__contains=value[0])
