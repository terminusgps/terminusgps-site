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
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = "/var/www/terminusgps-site/static/"
STATIC_URL = "/static/"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True

secret: dict[str, str] = get_secret("terminusgps-site-live-env", profile="Blake Nall")
SECRET_KEY = secret.get("SECRET_KEY")
MERCHANT_AUTH_LOGIN_ID = secret.get("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = secret.get("MERCHANT_AUTH_TRANSACTION_KEY")
TWILIO_TOKEN = secret.get("TWILIO_TOKEN")
TWILIO_SID = secret.get("TWILIO_SID")
TWILIO_MESSAGING_SID = secret.get("TWILIO_MESSAGING_SID")
TWILIO_FROM_NUMBER = secret.get("TWILIO_FROM_NUMBER")
WIALON_TOKEN = secret.get("WIALON_TOKEN")
WIALON_HOST = secret.get("WIALON_HOST")
WIALON_ADMIN_ID = secret.get("WIALON_ADMIN_ID")
WIALON_UNACTIVATED_GROUP = secret.get("WIALON_UNACTIVATED_GROUP")
EMAIL_HOST_USER = secret.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = secret.get("EMAIL_HOST_PASSWORD")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "support@terminusgps.com"

TRACKER_PROFILE = {
    "DISPLAY_NAME": "Terminus GPS",
    "EMAIL": {"SUPPORT": "support@terminusgps.com", "SALES": "sales@terminusgps.com"},
    "GITHUB": "https://github.com/terminus-gps/terminusgps-site/",
    "MOTD": "Check out the Terminus GPS mobile app!",
    "LEGAL_NAME": "Terminus GPS, LLC",
    "PHONE": {"OFFICE": "+17139045262", "SALES": ""},
    "ADDRESS": {
        "STREET": "17240 Huffmeister Road, Suite 103",
        "CITY": "Cypress",
        "STATE": "Texas",
        "ZIP": "77429",
        "COUNTRY": "USA",
    },
    "SOCIALS": {
        "FACEBOOK": {
            "display_name": "Terminus GPS",
            "profile_link": "https://www.facebook.com/TerminusGPSllc",
            "username": "TerminusGPSllc",
        },
        "INSTAGRAM": None,
        "NEXTDOOR": {
            "display_name": "TerminusGPS",
            "profile_link": "https://nextdoor.com/pages/terminusgps-cypress-tx/",
            "username": "TerminusGPS",
        },
        "TIKTOK": {
            "display_name": "TerminusGps",
            "profile_link": "https://www.tiktok.com/@terminusgps",
            "username": "terminusgps",
        },
        "TWITTER": None,
        "YOUTUBE": None,
    },
}

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
    "tailwind",
    "theme",
    "terminusgps_tracker.apps.TerminusgpsTrackerConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
