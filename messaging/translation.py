import simple_history
from modeltranslation.translator import register, TranslationOptions

from messaging.models import NotificationTemplate


@register(NotificationTemplate)
class NotificationTemplateTranslationOptions(TranslationOptions):
    fields = ('title', 'body')


simple_history.register(NotificationTemplate)
