import os
from terminusgps.settings.dev import *
os.environ["DJANGO_SETTINGS_MODULE"] = "terminusgps.settings.test"


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "bucket": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
        "OPTIONS": {
            "location": "media/"
        }
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test_db.sqlite3",
    },
}
