from time import time

from django.conf import settings
from django.contrib.auth.models import Permission

from .models import CustomPermission


def unique_id(prefix=''):
    return prefix + hex(int(time()))[2:10] + hex(int(time() * 1000000) % 0x100000)[2:7]


def get_permission_object_by_codename(codename):
    permission = Permission.objects.filter(codename=codename).first()
    return permission


def get_permission_list(code_names_list):
    permissions = Permission.objects.filter(codename__in=code_names_list)
    return permissions


def generate_permission(modules):
    perms = list()
    permissions = CustomPermission.objects.filter(x=modules)
    for permission in permissions:
        perm = tuple((permission.codename, permission.name))
        perms.append(perm)
    return tuple(perms)


def get_user_type(user):
    if user.is_staff:
        return settings.USER_TYPES['ADMIN']
    elif hasattr(user, 'staff'):
        return settings.USER_TYPES['STAFF']
    elif hasattr(user, 'accountstaff'):
        return settings.USER_TYPES['ACCOUNT_STAFF']
    else:
        return None
