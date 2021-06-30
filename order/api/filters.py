from django.db.models import Q
from django_filters import rest_framework as d_filters, DateTimeFromToRangeFilter

from order.models import Cart


class CartFilter(d_filters.FilterSet):
    name = d_filters.CharFilter(method='filter_name')
    account_id = d_filters.CharFilter(method='filter_account')
    customer_id = d_filters.CharFilter(method='filter_customer')
    payment_status = d_filters.CharFilter(method='filter_payment_status')
    reference = d_filters.CharFilter(lookup_expr='icontains')
    status = d_filters.CharFilter(method='filter_order_status')
    created_at = DateTimeFromToRangeFilter()

    class Meta:
        model = Cart
        fields = ()

    def filter_name(self, queryset, name, value):
        return queryset.filter(Q(customer__first_name__icontains=value) |
                               Q(customer__last_name__icontains=value) |
                               Q(customer__contact_no__icontains=value))

    def filter_account(self, queryset, name, value):
        return queryset.filter(account_id=value)

    def filter_customer(self, queryset, name, value):
        return queryset.filter(customer_id=value)

    def filter_payment_status(self, queryset, name, value):
        return queryset.filter(payment_status_id=value)

    def filter_order_status(self, queryset, name, value):
        return queryset.filter(status=value)
