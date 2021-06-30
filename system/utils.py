from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from system.models import ErrorMessage

from rest_framework.views import exception_handler


def get_errormessage(code=None):
    error = None
    if code and ErrorMessage.objects.filter(code=code).exists():
        error = dict()
        error['error_en'] = ErrorMessage.objects.get(code=code).name_en
        error['error_ar'] = ErrorMessage.objects.get(code=code).name_ar
    else:
        error = dict()
        error['error_en'] = "Invalid error code"
        error['error_er'] = ""
    return error


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if not response:
        context = get_errormessage("SYS-100")
        context.update({"error_filed": str(exc)})
        return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    error_message_dict = {
        status.HTTP_403_FORBIDDEN: get_errormessage('FORBIDDEN-100'),
        status.HTTP_500_INTERNAL_SERVER_ERROR: get_errormessage('SYS-100'),
        status.HTTP_400_BAD_REQUEST: get_errormessage('REQ-104') if 'error_en' not in response.data else response.data,
    }
    if isinstance(exc, Http404):
        response.data = get_errormessage("DOESNOTEXIST-100")
    else:
        error_message = error_message_dict.get(response.status_code, {})
        if response.data:
            response.data.update(error_message)
        else:
            response.data = error_message
    return response
