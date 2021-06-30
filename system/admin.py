from django.contrib import admin
from django.contrib.admin import register

from system.models import Account


@register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
