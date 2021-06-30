from django.db import models

from constants import CART_STATUS
from order.managers import OrderManager
from system.models import BaseModel, BaseModelBeforeHistory
from system.services import unique_id
from django.utils.translation import ugettext_lazy as _


class Cart(BaseModel):
    total = models.DecimalField(max_digits=18, decimal_places=3, verbose_name=_('Total'), default=0)
    country = models.ForeignKey("system.Country", null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey('customer.Customer', blank=True, null=True, on_delete=models.SET_NULL)
    account = models.ForeignKey('system.Account', blank=True, null=True, on_delete=models.SET_NULL)
    reference = models.CharField(max_length=255, unique=True)
    discount = models.DecimalField(max_digits=12, decimal_places=3, default=0, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    response_url = models.URLField(null=True, blank=True)
    failure_url = models.URLField(null=True, blank=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    order_date = models.DateTimeField(null=True, blank=True)
    payment_comments = models.TextField(null=True, blank=True)
    cart_status = models.ForeignKey("system.CartStatus", null=True, default=CART_STATUS.INITIATED, on_delete=models.SET_NULL)
    payment_status = models.ForeignKey("system.PaymentStatus", null=True, blank=True, on_delete=models.SET_NULL)
    otp = models.CharField(max_length=6, null=True, blank=True, editable=False)
    otp_expiry = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.reference = unique_id('REF')
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Contract {}".format(self.id)

    @property
    def count(self):
        return self.items.all().count()


class ProductType(BaseModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(BaseModelBeforeHistory):
    name = models.CharField(max_length=500, null=True, blank=True)
    product_type = models.ForeignKey(ProductType, related_name='products', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Item(BaseModel):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=18, decimal_places=3, verbose_name=_('Sale Price'))
    image_url = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Item {}".format(self.id)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')


class Order(Cart):
    objects = OrderManager()

    class Meta:
        proxy = True

