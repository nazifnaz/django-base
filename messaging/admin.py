from django.contrib import admin
from django.contrib.admin import register
from modeltranslation.admin import TabbedTranslationAdmin

from messaging.models import Notification, NotificationTemplate, NotificationConfiguration


@register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'rendered_message', 'when','status']


@register(NotificationTemplate)
class NotificationTemplateAdmin(TabbedTranslationAdmin):
    list_display = ['id', 'title', 'template_type', 'body']


@register(NotificationConfiguration)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_type', 'recipient']
