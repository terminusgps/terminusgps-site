from django.apps import AppConfig


class TerminusgpsTrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "terminusgps_tracker"
    verbose_name = "Terminus GPS Tracker"

    def ready(self):
        import terminusgps_tracker.signals
