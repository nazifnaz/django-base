from constants import DOWNLOAD_HANDLERS
from customer.api.views import CustomerViewSet

DOWNLOAD_HANDLER_CLASS = {
    DOWNLOAD_HANDLERS.MANAGE_CUSTOMER: CustomerViewSet,
}


def get_download_handler(id):
    return DOWNLOAD_HANDLER_CLASS[id]


def get_download_type(class_name):
    for key, value in DOWNLOAD_HANDLER_CLASS.items():
        if class_name == value:
            return key
    return None
