import decimal
import os
import sys
from pathlib import Path

from authorizenet.constants import constants
from django.contrib.messages import constants as messages
from terminusgps.wialon.flags import TokenFlag

os.umask(0)
decimal.getcontext().prec = 4
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FIELD_CLASS = "p-2 w-full bg-white dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300 group-has-[.errorlist]:text-red-800 group-has-[.errorlist]:bg-red-100"
DEFAULT_FROM_EMAIL = "support@terminusgps.com"
DEFAULT_TAX_RATE = decimal.Decimal(os.getenv("DEFAULT_TAX_RATE", "0.0825")) * 1
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
INTERNAL_IPS = ["127.0.0.1"]
LANGUAGE_CODE = "en-us"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/accounts/login/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
MERCHANT_AUTH_ENVIRONMENT = constants.SANDBOX
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
MERCHANT_AUTH_VALIDATION_MODE = "testMode"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
ROOT_URLCONF = "src.urls"
SECRET_KEY = "3ow7#%v3y*o&1wr6%!rt4%c7^^wlx%f8hkhn!#-gf%mk!_tf=^"
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
TIME_ZONE = "US/Central"
USE_I18N = True
USE_TZ = True
WIALON_ADMIN_ID = os.getenv("WIALON_ADMIN_ID")
WIALON_DEFAULT_PLAN = os.getenv("WIALON_DEFAULT_PLAN")
WIALON_TOKEN = os.getenv("WIALON_TOKEN")
WIALON_TOKEN_ACCESS_TYPE = (
    TokenFlag.VIEW_ACCESS
    | TokenFlag.MANAGE_NONSENSITIVE
    | TokenFlag.MANAGE_SENSITIVE
)
WSGI_APPLICATION = "src.wsgi.application"

ADMINS = [
    ("Peter", "pspeckman@terminusgps.com"),
    ("Blake", "blake@terminusgps.com"),
    ("Lili", "lili@terminusgps.com"),
]

MESSAGE_TAGS = {
    messages.ERROR: "text-red-800 dark:text-red-100 px-2 py-4 border-2 border-current rounded bg-red-100 dark:bg-red-600 flex items-center gap-2",
    messages.INFO: "text-gray-800 dark:text-gray-100 px-2 py-4 border-2 border-current rounded bg-gray-100 dark:bg-gray-600 flex items-center gap-2",
    messages.SUCCESS: "text-green-800 dark:text-green-100 px-2 py-4 border-2 border-current rounded bg-green-100 dark:bg-green-600 flex items-center gap-2",
    messages.WARNING: "text-yellow-800 dark:text-yellow-100 px-2 py-4 border-2 border-current rounded bg-yellow-100 dark:bg-yellow-300 flex items-center gap-2",
}


TRACKER_APP_CONFIG = {
    "DISPLAY_NAME": "Terminus GPS",
    "LEGAL_NAME": "Terminus GPS, LLC",
    "MOTD": "We know where ours are... do you?",
    "REPOSITORY_URL": "https://github.com/terminusgps/terminusgps-site/",
    "HOSTING_URL": "https://hosting.terminusgps.com/",
    "MOBILE_APPS": {
        "IOS": {
            "url": "https://apps.apple.com/us/app/terminus-gps-mobile/id1419439009?ls=1",
            "badge": "terminusgps/img/App_Store_Badge_Black.svg",
        },
        "ANDROID": {
            "url": "https://play.google.com/store/apps/details?id=com.terminusgps.track&hl=en",
            "badge": "terminusgps/img/Play_Store_Badge_White.png",
        },
    },
    "SOCIALS": {
        "FACEBOOK": {
            "display_name": "Terminus GPS",
            "link": "https://www.facebook.com/TerminusGPSllc",
            "username": "TerminusGPSllc",
            "icon": "terminusgps/icon/facebook.svg",
        },
        "TIKTOK": {
            "display_name": "TerminusGps",
            "link": "https://www.tiktok.com/@terminusgps",
            "username": "terminusgps",
            "icon": "terminusgps/icon/tiktok.svg",
        },
        "NEXTDOOR": {
            "display_name": "TerminusGPS",
            "link": "https://nextdoor.com/pages/terminusgps-cypress-tx/",
            "username": "TerminusGPS",
            "icon": "terminusgps/icon/nextdoor.svg",
        },
        "TWITTER": {
            "display_name": "TERMINUSGPS",
            "link": "https://x.com/TERMINUSGPS",
            "username": "TERMINUSGPS",
            "icon": "terminusgps/icon/twitter.svg",
        },
    },
}


STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
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
    "terminusgps_payments.apps.TerminusgpsPaymentsConfig",
    "terminusgps_notifications.apps.TerminusgpsNotificationsConfig",
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "simple",
        }
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "authorizenet.sdk": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

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
