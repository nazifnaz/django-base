from django.db import models

from constants import CART_STATUS


class OrderManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(cart_status=CART_STATUS.ORDER)
