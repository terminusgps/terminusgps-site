from django.apps import AppConfig
from django.db.models.signals import post_save


class TerminusgpsTrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "terminusgps_tracker"
    verbose_name = "Terminus GPS Tracker"

    def ready(self):
        from . import models, signals

        post_save.connect(
            signals.update_customer_subscription_amount,
            sender=models.CustomerWialonUnit,
        )
