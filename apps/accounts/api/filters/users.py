"""Users filters"""

from django_filters import FilterSet, CharFilter, OrderingFilter

from apps.accounts.models import User
from gestion_consultas.utils import filter_by_full_name


class UserFilter(FilterSet):
    """Appointment filter"""

    username = CharFilter(field_name='username', lookup_expr='unaccent__icontains')
    identification_number = CharFilter(field_name='identification_number', lookup_expr='unaccent__icontains')
    full_name = CharFilter(method='filter_by_full_name')

    class Meta:
        model = User
        fields = [
            'identification_type', 'role', 'is_active', 'is_superuser', 'created_at', 'updated_at'
        ]

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )

    @classmethod
    def filter_by_full_name(cls, queryset, name, value):
        return filter_by_full_name(queryset, 'first_name', 'last_name', value)
