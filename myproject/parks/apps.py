from django.apps import AppConfig

class ParksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parks'

    def ready(self):
        import parks.signals
