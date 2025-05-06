import decimal
import logging
import os
import pathlib

from terminusgps.aws.secrets import get_secret

os.umask(0)
secret: dict[str, str] = get_secret("terminusgps-site-live-env")
db_secret: dict[str, str] = get_secret("rds!db-90c204bb-fdaf-483f-9305-66a13050cf3e")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = [".terminusgps.com"]
CSRF_COOKIE_SECURE = True
DEBUG = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FROM_EMAIL = "noreply@terminusgps.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
LOGIN_URL = "/login/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
ROOT_URLCONF = "src.urls"
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
WSGI_APPLICATION = "src.wsgi.application"

# Secret values
DEFAULT_TAX_RATE = decimal.Decimal(
    secret.get("DEFAULT_TAX_RATE", "0.0825"),
    context=decimal.Context(prec=4, rounding=decimal.ROUND_HALF_UP),
)
EMAIL_HOST_PASSWORD = secret.get("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = secret.get("EMAIL_HOST_USER")
MERCHANT_AUTH_LOGIN_ID = secret.get("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = secret.get("MERCHANT_AUTH_TRANSACTION_KEY")
SECRET_KEY = secret.get("SECRET_KEY")
TRACKER_ENCRYPTION_KEY = secret.get("TRACKER_ENCRYPTION_KEY")
TWILIO_FROM_NUMBER = secret.get("TWILIO_FROM_NUMBER")
TWILIO_MESSAGING_SID = secret.get("TWILIO_MESSAGING_SID")
TWILIO_SID = secret.get("TWILIO_SID")
TWILIO_TOKEN = secret.get("TWILIO_TOKEN")
WIALON_ADMIN_ID = secret.get("WIALON_ADMIN_ID")
WIALON_DEFAULT_PLAN = secret.get("WIALON_DEFAULT_PLAN")
WIALON_HOST = secret.get("WIALON_HOST")
WIALON_SESSION_LOGLEVEL = logging.WARNING
WIALON_TOKEN = secret.get("WIALON_TOKEN")
WIALON_UNACTIVATED_GROUP = secret.get("WIALON_UNACTIVATED_GROUP")

TRACKER_APP_CONFIG = {
    "DISPLAY_NAME": "Terminus GPS",
    "LEGAL_NAME": "Terminus GPS, LLC",
    "MOTD": "Check out the Terminus GPS mobile app!",
    "REPOSITORY_URL": "https://github.com/terminusgps/terminusgps-site/",
    "HOSTING_URL": "https://hosting.terminusgps.com/",
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
            "verify": "/home/ubuntu/terminusgps-site/.venv/lib/python3.12/site-packages/certifi/cacert.pem",
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
    "terminusgps_tracker.apps.TerminusgpsTrackerConfig",
    "terminusgps_install.apps.TerminusgpsInstallConfig",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_secret.get("username"),
        "HOST": "terminusgps-db-1.cl0u0gis0s3x.us-east-1.rds.amazonaws.com",
        "USER": db_secret.get("username"),
        "PASSWORD": db_secret.get("password"),
        "PORT": 5432,
        "OPTIONS": {"client_encoding": "UTF8"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
