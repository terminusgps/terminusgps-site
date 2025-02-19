import logging
import os
import pathlib
from terminusgps.aws.secrets import get_secret

os.umask(0)
secret: dict[str, str] = get_secret("terminusgps-site-live-env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
ALLOWED_HOSTS = [".terminusgps.com"]
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
CSRF_COOKIE_SECURE = True
DEBUG = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FROM_EMAIL = "support@terminusgps.com"
DOCS_ACCESS = "staff"
DOCS_ROOT = BASE_DIR.parent / "docs/build/html"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_HOST_PASSWORD = secret.get("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = secret.get("EMAIL_HOST_USER")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
MERCHANT_AUTH_LOGIN_ID = secret.get("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = secret.get("MERCHANT_AUTH_TRANSACTION_KEY")
SECRET_KEY = secret.get("SECRET_KEY")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = "/var/www/terminusgps-site/static/"
STATIC_URL = "/static/"
TIME_ZONE = "America/Chicago"
TWILIO_FROM_NUMBER = secret.get("TWILIO_FROM_NUMBER")
TWILIO_MESSAGING_SID = secret.get("TWILIO_MESSAGING_SID")
TWILIO_SID = secret.get("TWILIO_SID")
TWILIO_TOKEN = secret.get("TWILIO_TOKEN")
USE_I18N = True
USE_TZ = True
WIALON_ADMIN_ID = secret.get("WIALON_ADMIN_ID")
WIALON_HOST = secret.get("WIALON_HOST")
WIALON_TOKEN = secret.get("WIALON_TOKEN")
WIALON_UNACTIVATED_GROUP = secret.get("WIALON_UNACTIVATED_GROUP")
WIALON_DEFAULT_PLAN = secret.get("WIALON_DEFAULT_PLAN")
WIALON_SESSION_LOGLEVEL = logging.WARNING
TRACKER_ENCRYPTION_KEY = secret.get("TRACKER_ENCRYPTION_KEY")

TRACKER_APP_CONFIG = {
    "DISPLAY_NAME": "Terminus GPS",
    "LEGAL_NAME": "Terminus GPS, LLC",
    "MOTD": "Check out the Terminus GPS mobile app!",
    "REPOSITORY_URL": "https://github.com/terminusgps/terminusgps-site/",
    "ADDRESSES": [
        {
            "NAME": "OFFICE1",
            "OPTIONS": {
                "street": "17240 Huffmeister Road, Suite 103",
                "city": "Cypress",
                "state": "Texas",
                "zip": "77429",
                "country": "USA",
            },
        },
        {
            "NAME": "OFFICE2",
            "OPTIONS": {
                "street": "17240 Huffmeister Road, Suite 103",
                "city": "Cypress",
                "state": "Texas",
                "zip": "77429",
                "country": "USA",
            },
        },
    ],
    "PHONES": [
        {"OFFICE": "+17139045262"},
        {"SALES": "+17139045262"},
        {"SUPPORT": "+17139045262"},
    ],
    "EMAILS": [
        {
            "NAME": "SALES",
            "OPTIONS": {
                "address": "sales@terminusgps.com",
                "link": "mailto:sales@terminusgps.com",
            },
        },
        {
            "NAME": "SUPPORT",
            "OPTIONS": {
                "address": "support@terminusgps.com",
                "link": "mailto:support@terminusgps.com",
            },
        },
    ],
    "SOCIALS": [
        {
            "NAME": "Facebook",
            "OPTIONS": {
                "display_name": "Terminus GPS",
                "profile_link": "https://www.facebook.com/TerminusGPSllc",
                "username": "TerminusGPSllc",
                "icon": "terminusgps_tracker/icons/facebook.svg",
            },
        },
        {
            "NAME": "TikTok",
            "OPTIONS": {
                "display_name": "TerminusGps",
                "profile_link": "https://www.tiktok.com/@terminusgps",
                "username": "terminusgps",
                "icon": "terminusgps_tracker/icons/tiktok.svg",
            },
        },
        {
            "NAME": "Nextdoor",
            "OPTIONS": {
                "display_name": "TerminusGPS",
                "profile_link": "https://nextdoor.com/pages/terminusgps-cypress-tx/",
                "username": "TerminusGPS",
                "icon": "terminusgps_tracker/icons/nextdoor.svg",
            },
        },
        {
            "NAME": "Twitter",
            "OPTIONS": {
                "display_name": "TERMINUSGPS",
                "profile_link": "https://x.com/TERMINUSGPS",
                "username": "TERMINUSGPS",
                "icon": "terminusgps_tracker/icons/twitter.svg",
            },
        },
    ],
    "SUBSCRIPTIONS": [
        {"NAME": "Basic", "OPTIONS": {"cmd": "Basic", "amount": "19.99"}},
        {"NAME": "Standard", "OPTIONS": {"cmd": "Standard", "amount": "29.99"}},
        {"NAME": "Premium", "OPTIONS": {"cmd": "Premium", "amount": "39.99"}},
    ],
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
            "bucket_name": "terminusgps-site-bucket",
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
    "docs",
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

ROOT_URLCONF = "src.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "src.wsgi.application"

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
