import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings.prod")

app = Celery("src")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_subscription_days_updates(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        subscription_days_update.s("Updating days..."),
    )


@app.task
def subscription_days_update(x):
    print(x)
