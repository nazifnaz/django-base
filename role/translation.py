import simple_history
from modeltranslation.translator import register, TranslationOptions

from role.models import Role, CustomPermission


@register(Role)
class RoleTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(CustomPermission)
class PermissionTranslationOptions(TranslationOptions):
    fields = ('name', 'model_name')


simple_history.register(Role)
simple_history.register(CustomPermission)
