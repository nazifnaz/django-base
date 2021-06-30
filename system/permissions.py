
from rest_framework.permissions import BasePermission

import settings


class GLOBAL_PERMISION(BasePermission):
    def has_permission(self, request, view):
        # API_KEY should be in request headers to authenticate requests
        api_key_secret = request.META.get('HTTP_X_API_KEY', None)

        return api_key_secret == settings.API_KEY


class CUSTOMER_PERMISION(BasePermission):
    def has_permission(self, request, view):
        # API_KEY should be in request headers to authenticate requests
        token = request.META.get('HTTP_AUTHORIZATION', None)
        # if toke:
        return token == settings.API_KEY