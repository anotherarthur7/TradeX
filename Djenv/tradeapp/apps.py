from django.apps import AppConfig


class TradeappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tradeapp'

    def ready(self):
        # Import and connect the signal
        import tradeapp.signals

class YourAppConfig(AppConfig):
    name = 'your_app_name'

    def ready(self):
        import your_app_name.signals