import simple_history
from modeltranslation.translator import register, TranslationOptions
from .models import Product


@register(Product)
class ItemTranslationOptions(TranslationOptions):
    fields = ('name',)


simple_history.register(Product)

