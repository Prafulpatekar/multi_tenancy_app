from django.apps import AppConfig


class VendorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendor_app'

    def ready(self):
        import vendor_app.signals
