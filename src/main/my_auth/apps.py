from django.apps import AppConfig


class MyAuthConfig(AppConfig):
    """
    Конфиг авторизации
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "my_auth"
    verbose_name = "Авторизация"