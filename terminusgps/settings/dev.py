import os
import pathlib
import sys

from django.contrib.messages import constants as message_constants

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".awswaf.com"]

ADMINS = [
    ("Peter", "pspeckman@terminusgps.com"),
    ("Blake", "blake@terminusgps.com"),
]

DEBUG = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FROM_EMAIL = "noreply@terminusgps.com"

DEFAULT_REPLY_TO_EMAIL = "support@terminusgps.com"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]

LANGUAGE_CODE = "en-us"

LOGIN_REDIRECT_URL = "/"

LOGIN_URL = "/accounts/login/"

MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "media/"

MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")

MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")

MERCHANT_AUTH_ENVIRONMENT = "liveMode"

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

ROOT_URLCONF = "terminusgps.urls"

SECRET_KEY = "3ow7#%v3y*o&1wr6%!rt4%c7^^wlx%f8hkhn!#-gf%mk!_tf=^"

SECURE_CROSS_ORIGIN_OPENER_POLICY = "unsafe-none"

SESSION_COOKIE_HTTPONLY = True

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = "static/"

TIME_ZONE = "America/Chicago"

USE_I18N = False

USE_TZ = True

WSGI_APPLICATION = "terminusgps.wsgi.application"

WIALON_TOKEN = os.getenv("WIALON_TOKEN")

MESSAGE_TAGS = {
    message_constants.DEBUG: "p-2 bg-gray-50 text-gray-700 border border-current rounded",
    message_constants.INFO: "p-2 bg-gray-50 text-gray-700 border border-current rounded",
    message_constants.SUCCESS: "p-2 bg-green-50 text-green-700 border border-current rounded",
    message_constants.WARNING: "p-2 bg-yellow-50 text-yellow-700 border border-current rounded",
    message_constants.ERROR: "p-2 bg-red-50 text-red-700 border border-current rounded",
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

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#     }
# }

TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
        "QUEUES": ["default"],
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.forms",
    "phonenumber_field",
    "terminusgps_site.apps.TerminusgpsSiteConfig",
    "terminusgps_installer.apps.TerminusgpsInstallerConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
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
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "authorizenet": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "asyncio": {"level": "CRITICAL"},
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

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME"),
#         "HOST": os.getenv("DB_HOST"),
#         "USER": os.getenv("DB_USERNAME"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
#         "PORT": os.getenv("DB_PORT", 5432),
#         "OPTIONS": {"client_encoding": "UTF8"},
#         "CONN_MAX_AGE": None,
#     }
# }

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
