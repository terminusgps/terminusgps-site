from terminusgps.settings.dev import *

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings.test")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    "bucket": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
        "OPTIONS": {"location": "media/"},
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}
