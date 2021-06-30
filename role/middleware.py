from django.contrib.auth.models import Permission
from django.http import JsonResponse
from django_currentuser.middleware import get_current_user
from rest_framework import status

from .models import CustomPermission


class CustomPermissionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.resolver_match:
            return response
        code_name = request.resolver_match.url_name
        if request.method in ['PATCH', 'PUT']:
            request_method = 'update'
        elif request.method == 'POST':
            request_method = 'create'
        else:
            request_method = request.method.lower()
        combined_code = f"{request_method}_{code_name}"
        custom_permission = CustomPermission.objects.filter(codename__in=[combined_code, code_name])
        if not custom_permission:
            return response
        current_user = get_current_user()

        if current_user:
            groups = list(current_user.groups.values_list('id', flat=True))
            permissions = list(
                Permission.objects.filter(group__in=groups).distinct().values_list('codename', flat=True))
            if code_name not in permissions and combined_code not in permissions:
                return JsonResponse({'error_en': 'Permission Denied', "error_ar": "طلب الاذن مرفوض"},
                                    status=status.HTTP_403_FORBIDDEN)
        return response
