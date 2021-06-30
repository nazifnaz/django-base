from rest_framework.permissions import BasePermission


class IsAccount(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    (request.user.is_staff or hasattr(request.user, 'accountstaff')))


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    (request.user.is_staff or hasattr(request.user, 'customer')))
