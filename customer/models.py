import random
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from rest_framework import status

from constants import DEFAULT_COUNTRY_ID
from system.models import BaseModel


from system.paths import get_profile_path


class Customer(BaseModel):
    GENDER_CHOICES = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Others'),
    )
    first_name = models.CharField(max_length=500, null=True, blank=True)
    last_name = models.CharField(max_length=500, null=True, blank=True)
    contact_no = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)
    verified = models.BooleanField(default=True)
    profile_pic = models.ImageField(upload_to=get_profile_path, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    otp = models.CharField(max_length=6, null=True, blank=True, editable=False)
    otp_expiry = models.DateTimeField(null=True, blank=True, editable=False)
    verified_at = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return self.name + "(" + self.contact_no + ")"

    @property
    def email(self):
        return self.user.email

    @property
    def name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

    def save(self, *args, **kwargs):
        s = self.contact_no
        if s:
            contact_no = (s[1:] if s.startswith('0') else s)
            self.contact_no = contact_no if self.contact_no else None
        super().save(*args, **kwargs)

    def generate_otp(self):
        otp = ''.join(random.choice('1234567890') for i in range(6))
        self.otp = otp
        self.otp_expiry = datetime.now() + timedelta(minutes=15.0)
        self.save()
        return otp

    def verify_otp(self, otp, verify=False, response_code="OTP-100", response_status=status.HTTP_400_BAD_REQUEST):
        if otp and otp == self.otp and self.otp_expiry >= datetime.now(self.otp_expiry.tzinfo):
            if verify:
                self.verified = True
                self.verified_at = timezone.now()
                self.save()
            response_code = "OTP-103"
            response_status = status.HTTP_202_ACCEPTED
        return response_code, response_status


class Address(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=400, null=True, blank=True, default='')
    city = models.CharField(max_length=100, null=True, blank=True, default='')
    country = models.ForeignKey("system.Country", blank=True, null=True, on_delete=models.SET_NULL)
    area = models.ForeignKey("system.Area", blank=True, null=True, default=DEFAULT_COUNTRY_ID,
                             on_delete=models.SET_NULL)
    notes = models.TextField('Notes', help_text="notes", null=True, blank=True, default='')
    default = models.BooleanField(default=False)
    customer = models.ForeignKey('customer.Customer', related_name='addresses', blank=True, null=True,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return str(self.area) + "-" + str(self.country)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Address'
