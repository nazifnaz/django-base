from django.db.models import Q
from django_filters import rest_framework as d_filters

from system.models import DownloadJob, Account, AccountStaff


class DownloadJobFilter(d_filters.FilterSet):

    class Meta:
        model = DownloadJob
        fields = ("download_type", "status")


class AccountFilter(d_filters.FilterSet):
    name = d_filters.CharFilter(lookup_expr='icontains')
    address = d_filters.CharFilter(lookup_expr='icontains')
    reference = d_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ()


class AccountStaffFilter(d_filters.FilterSet):
    name = d_filters.CharFilter(method='filter_name')
    email = d_filters.CharFilter(method='filter_email')
    role_id = d_filters.CharFilter(method='filter_role')
    contact_no = d_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AccountStaff
        fields = ()

    def filter_name(self, queryset, name, value):
        return queryset.filter(Q(user__first_name__icontains=value) |
                               Q(user__last_name__icontains=value))

    def filter_email(self, queryset, name, value):
        return queryset.filter(user__email__icontains=value)

    def filter_role(self, queryset, name, value):
        return queryset.filter(role=value)
