import os
from pathlib import Path

from terminusgps.aws import get_secret

os.umask(0)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = [".terminusgps.com"]
CLIENT_NAME = "Terminus GPS"
CSRF_COOKIE_SECURE = True
DEBUG = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
FORM_RENDERER = "terminusgps_tracker.forms.TerminusFormRenderer"
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
SECRET_KEY = get_secret("terminusgps-site-key")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = "/var/www/terminusgps-site/static/"
STATIC_URL = "/static/"
TIME_ZONE = "America/Chicago"
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_MESSAGING_SID = os.getenv("TWILIO_MESSAGING_SID")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
USE_I18N = True
USE_TZ = True
WIALON_API_TOKEN = os.getenv("WIALON_API_TOKEN")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "debug.log",
        }
    },
    "loggers": {"django": {"handlers": ["file"], "level": "DEBUG", "propagate": True}},
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "session_profile": "Blake Nall",
            "bucket_name": "terminusgps-bucket",
            "location": "static/",
            "region_name": "us-east-1",
            "verify": False,
        },
    },
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.forms",
    "django_browser_reload",
    "django_htmx",
    "tailwind",
    "terminusgps_tracker.apps.TerminusgpsTrackerConfig",
    "theme",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "terminusgps.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "/forms/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "terminusgps.wsgi.application"

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
