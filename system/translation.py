import simple_history
from modeltranslation.translator import register, TranslationOptions

from system.models import *


@register(DocumentType)
class DocumentTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Area)
class AreaTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(CartStatus)
class ContractStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ErrorMessage)
class ErrorMessageTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(PaymentStatus)
class PaymentStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


simple_history.register(Area)
simple_history.register(Country)
simple_history.register(ErrorMessage)
simple_history.register(DocumentType)
