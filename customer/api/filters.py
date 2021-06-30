from django.db.models import Q
from django_filters import rest_framework as d_filters

from customer.models import Customer


class CustomerFilter(d_filters.FilterSet):
    name = d_filters.CharFilter(method='filter_name')
    contact_no = d_filters.CharFilter(lookup_expr='icontains')
    email = d_filters.CharFilter(method='filter_email')

    class Meta:
        model = Customer
        fields = ()

    def filter_name(self, queryset, name, value):
        return queryset.filter(Q(first_name__icontains=value) |
                               Q(last_name__icontains=value))

    def filter_email(self, queryset, name, value):
        return queryset.filter(user__email__icontains=value)
