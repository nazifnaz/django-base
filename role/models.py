from django.contrib.auth.models import Group
from django.db import models

from system.models import BaseModelBeforeHistory


class UserType(BaseModelBeforeHistory):

    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Role(BaseModelBeforeHistory):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250, null=True, blank=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True, blank=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CustomPermission(BaseModelBeforeHistory):
    model_name = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    codename = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.ManyToManyField(UserType)

    def __str__(self):
        return self.name
