from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.home"

    def ready(self):
        import urbanvitaliz.apps.home.signals  # noqa
        from actstream import registry
        from django.contrib.auth.models import User

        registry.register(User)
