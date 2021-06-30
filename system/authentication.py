from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from system.models import BlackListedToken


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        if BlackListedToken.objects.filter(token=raw_token).exists():
            raise InvalidToken()
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        if not self.is_user_active(user):
            self.black_list(request)
            return None
        return user, validated_token

    def black_list(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        BlackListedToken.objects.get_or_create(token=raw_token, user=self.get_user(validated_token))
        return None

    def is_user_active(self, user):
        if hasattr(user, 'staff') and user.staff:
            return user.staff.is_active
        elif hasattr(user, 'accountstaff') and user.accountstaff:
            if not user.accountstaff.account.is_active:
                return False
            return user.accountstaff.is_active
        elif hasattr(user, 'customer') and user.customer:
            return user.customer.active
        elif user.is_staff:
            return True
        else:
            return False
