from django.apps import AppConfig


class RoleConfig(AppConfig):
    name = 'role'

    def ready(self):
        import role.signals
