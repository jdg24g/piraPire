import django_filters
from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    # Rango de fechas
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Rango de montos
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    # Búsqueda de texto en descripción
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Transaction
        fields = ['wallet', 'category', 'type', 'subtype', 'date_from', 'date_to', 'amount_min', 'amount_max', 'description']
