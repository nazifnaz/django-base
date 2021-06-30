from django.contrib import admin
from django.contrib.admin import register

from system.models import AccountStaff
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'contact_no')
    search_fields = ('first_name', 'last_name', 'contact_no')
    list_per_page = 20


class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'area', 'customer',)
    search_fields = ('country__name', 'name', 'area__name', 'customer__contact_no', 'customer__first_name')
    list_per_page = 20

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs['labels'] = {'addresss': 'Address'}
        return super().get_form(request, obj=obj, change=change, **kwargs)


@register(AccountStaff)
class AccountstaffAdmin(admin.ModelAdmin):
    list_display = ['id']


admin.site.register(Address, AddressAdmin)
admin.site.register(Customer, CustomerAdmin)
