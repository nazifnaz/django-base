import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from role.models import CustomPermission


logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomPermission)
def add_custom_permissions(sender, instance, created, **kwargs):
    if created:
        try:
            Permission.objects.get_or_create(name=instance.name, codename=instance.codename,
                                             content_type=ContentType.objects.get(model=instance.model_name.lower()))
        except Exception as e:
            logger.error('Unable to create permissions. %s' % e)
