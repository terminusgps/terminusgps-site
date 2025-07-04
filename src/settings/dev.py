import decimal
import logging
import os
from pathlib import Path

from authorizenet.constants import constants

os.umask(0)

secret: dict[str, str | None] = {
    "SECRET_KEY": os.getenv("SECRET_KEY"),
    "CONNECT_SECRET": os.getenv("CONNECT_SECRET"),
    "DEFAULT_TAX_RATE": os.getenv("DEFAULT_TAX_RATE", "0.085"),
    "TWILIO_TOKEN": os.getenv("TWILIO_TOKEN"),
    "TWILIO_SID": os.getenv("TWILIO_SID"),
    "TWILIO_MESSAGING_SID": os.getenv("TWILIO_MESSAGING_SID"),
    "TWILIO_FROM_NUMBER": os.getenv("TWILIO_FROM_NUMBER"),
    "WIALON_TOKEN": os.getenv("WIALON_TOKEN"),
    "WIALON_HOST": os.getenv("WIALON_HOST"),
    "WIALON_ADMIN_ID": os.getenv("WIALON_ADMIN_ID"),
    "WIALON_UNACTIVATED_GROUP": os.getenv("WIALON_UNACTIVATED_GROUP"),
    "WIALON_DEFAULT_PLAN": os.getenv("WIALON_DEFAULT_PLAN"),
    "TRACKER_ENCRYPTION_KEY": os.getenv("TRACKER_ENCRYPTION_KEY"),
    "EMAIL_HOST_USER": os.getenv("EMAIL_HOST_USER"),
    "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD"),
    "WIALON_ADMIN_ACCOUNT": os.getenv("WIALON_ADMIN_ACCOUNT"),
    "MERCHANT_AUTH_LOGIN_ID": os.getenv("MERCHANT_AUTH_LOGIN_ID"),
    "MERCHANT_AUTH_TRANSACTION_KEY": os.getenv(
        "MERCHANT_AUTH_TRANSACTION_KEY"
    ),
}


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_FIELD_CLASS = "p-2 w-full bg-white dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300 group-has-[.errorlist]:text-red-800 group-has-[.errorlist]:bg-red-100"
LOGIN_URL = "/login/"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
DOCS_ACCESS = "public"
DOCS_ROOT = BASE_DIR.parent / "docs" / "build" / "html"
CONNECT_SECRET = secret.get("CONNECT_SECRET")
CORS_ORIGIN_ALLOW_ALL = True
DEBUG = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FROM_EMAIL = "support@terminusgps.com"
FORM_RENDERER = "terminusgps.django.forms.renderer.TerminusgpsFormRenderer"
DEFAULT_TAX_RATE = decimal.Decimal(
    secret.get("DEFAULT_TAX_RATE", "0.085"),
    context=decimal.Context(prec=4, rounding=decimal.ROUND_HALF_UP),
)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
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
MERCHANT_AUTH_ENVIRONMENT = constants.SANDBOX
MERCHANT_AUTH_VALIDATION_MODE = "testMode"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
ROOT_URLCONF = "src.urls"
SECRET_KEY = "3ow7#%v3y*o&1wr6%!rt4%c7^^wlx%f8hkhn!#-gf%mk!_tf=^"
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
TIME_ZONE = "US/Central"
TRACKER_ENCRYPTION_KEY = secret.get("TRACKER_ENCRYPTION_KEY")
TWILIO_FROM_NUMBER = secret.get("TWILIO_FROM_NUMBER")
TWILIO_MESSAGING_SID = secret.get("TWILIO_MESSAGING_SID")
TWILIO_SID = secret.get("TWILIO_SID")
TWILIO_TOKEN = secret.get("TWILIO_TOKEN")
USE_I18N = True
USE_TZ = True
WIALON_ADMIN_ID = secret.get("WIALON_ADMIN_ID")
WIALON_DEFAULT_PLAN = secret.get("WIALON_DEFAULT_PLAN")
WIALON_HOST = secret.get("WIALON_HOST")
WIALON_SESSION_LOGLEVEL = logging.DEBUG
WIALON_TOKEN = secret.get("WIALON_TOKEN")
WIALON_UNACTIVATED_GROUP = secret.get("WIALON_UNACTIVATED_GROUP")
WIALON_ADMIN_ACCOUNT = secret.get("WIALON_ADMIN_ACCOUNT")
WSGI_APPLICATION = "src.wsgi.application"


TRACKER_APP_CONFIG = {
    "DISPLAY_NAME": "Terminus GPS",
    "LEGAL_NAME": "Terminus GPS, LLC",
    "MOTD": "We know where ours are... do you?",
    "REPOSITORY_URL": "https://github.com/terminusgps/terminusgps-site/",
    "HOSTING_URL": "https://hosting.terminusgps.com/",
    "SOCIALS": {
        "FACEBOOK": {
            "display_name": "Terminus GPS",
            "link": "https://www.facebook.com/TerminusGPSllc",
            "username": "TerminusGPSllc",
            "icon": "terminusgps/icons/facebook.svg",
        },
        "TIKTOK": {
            "display_name": "TerminusGps",
            "link": "https://www.tiktok.com/@terminusgps",
            "username": "terminusgps",
            "icon": "terminusgps/icons/tiktok.svg",
        },
        "NEXTDOOR": {
            "display_name": "TerminusGPS",
            "link": "https://nextdoor.com/pages/terminusgps-cypress-tx/",
            "username": "TerminusGPS",
            "icon": "terminusgps/icons/nextdoor.svg",
        },
        "TWITTER": {
            "display_name": "TERMINUSGPS",
            "link": "https://x.com/TERMINUSGPS",
            "username": "TERMINUSGPS",
            "icon": "terminusgps/icons/twitter.svg",
        },
    },
}


STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

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
    "terminusgps_installer.apps.TerminusgpsInstallerConfig",
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


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]
