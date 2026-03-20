from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
    verbose_name = "Каталог моделей"

    def ready(self) -> None:
        # Регистрация сигналов (импорт для побочного эффекта @receiver)
        import catalog.signals  # noqa: F401
