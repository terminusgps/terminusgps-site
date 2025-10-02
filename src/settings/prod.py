import decimal
import logging.config
import os
import pathlib
from socket import gethostbyname, gethostname

from authorizenet.constants import constants
from django.contrib.messages import constants as messages

os.umask(0)
decimal.getcontext().prec = 4
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

ALLOWED_HOSTS = [
    ".terminusgps.com",
    ".elb.amazonaws.com",
    gethostbyname(gethostname()),
]
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["https://*.terminusgps.com", "https://terminusgps.com"]
DEBUG = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_CHARSET = "utf-8"
DEFAULT_FIELD_CLASS = "p-2 w-full bg-white dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300 group-has-[.errorlist]:text-red-800 group-has-[.errorlist]:bg-red-100"
DEFAULT_FROM_EMAIL = "support@terminusgps.com"
DEFAULT_TAX_RATE = decimal.Decimal(os.getenv("DEFAULT_TAX_RATE", "0.0825")) * 1
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "email-smtp.us-east-1.amazonaws.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
FILE_CHARSET = "utf-8"
LANGUAGE_CODE = "en-us"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/accounts/login/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
MERCHANT_AUTH_ENVIRONMENT = constants.PRODUCTION
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
MERCHANT_AUTH_VALIDATION_MODE = "liveMode"
ROOT_URLCONF = "src.urls"
SECRET_KEY = os.getenv("SECRET_KEY")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
TIME_ZONE = "US/Central"
USE_I18N = True
USE_TZ = True
USE_X_FORWARDED_HOST = True
WIALON_ADMIN_ID = os.getenv("WIALON_ADMIN_ID", "27881459")
WIALON_DEFAULT_PLAN = os.getenv("WIALON_DEFAULT_PLAN", "terminusgps_ext_hist")
WIALON_TOKEN = os.getenv("WIALON_TOKEN")
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
            "badge": "terminusgps/App_Store_Badge_Black.svg",
        },
        "ANDROID": {
            "url": "https://play.google.com/store/apps/details?id=com.terminusgps.track&hl=en",
            "badge": "terminusgps/Play_Store_Badge_White.png",
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

LOGGING_CONFIG = None
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "generic": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                "class": "logging.Formatter",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "authorizenet.sdk": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": True,
            },
            "gunicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }
)

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.getenv(
                "AWS_S3_BUCKET_NAME", "terminusgps-site-bucket"
            ),
            "location": os.getenv("AWS_S3_BUCKET_LOCATION", "static/"),
            "region_name": os.getenv("AWS_S3_BUCKET_REGION", "us-east-1"),
            "verify": os.getenv(
                "AWS_S3_CERT_PATH",
                ".venv/lib/python3.12/site-packages/certifi/cacert.pem",
            ),
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "TIMEOUT": 60 * 15,
    }
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
        "NAME": os.getenv("DB_NAME"),
        "HOST": os.getenv("DB_HOST"),
        "USER": os.getenv("DB_USERNAME"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "PORT": os.getenv("DB_PORT", 5432),
        "OPTIONS": {"client_encoding": "UTF8"},
        "CONN_MAX_AGE": None,
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
