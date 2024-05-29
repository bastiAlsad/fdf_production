from django.apps import AppConfig


class FdfAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fdf_app'
    def ready(self):
        import fdf_app.signals
