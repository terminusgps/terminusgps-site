import base64
import json
import logging.config
import os
import pathlib
import socket
import sys

import boto3

session = boto3.session.Session()
client = session.client(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    service_name="secretsmanager",
    region_name="us-east-1",
)
get_secret_value_response = client.get_secret_value(
    SecretId="terminusgps-site/env"
)
if "SecretString" in get_secret_value_response:
    secret_value = get_secret_value_response["SecretString"]
else:
    secret_value = base64.b64decode(get_secret_value_response["SecretBinary"])
secrets = json.loads(secret_value)


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = [
    "terminusgps.com",
    ".terminusgps.com",
    ".elb.amazonaws.com",
    ".s3.amazonaws.com",
    ".awswaf.com",
    socket.gethostbyname(socket.gethostname()),
]

ADMINS = ["pspeckman3@terminusgps.com", "blake@terminusgps.com"]

CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://terminusgps.com",
    "https://api.terminusgps.com",
    "https://app.terminusgps.com",
    "https://media.terminusgps.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://terminusgps.com",
    "https://api.terminusgps.com",
    "https://app.terminusgps.com",
    "https://media.terminusgps.com",
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000

DOCS_ROOT = BASE_DIR / "docs" / "build" / "html"

DOCS_ACCESS = "login_required"

DEBUG = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_CHARSET = "utf-8"

DEFAULT_FROM_EMAIL = "noreply@terminusgps.com"

DEFAULT_REPLY_TO_EMAIL = "support@terminusgps.com"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = secrets.get("EMAIL_HOST", "email-smtp.us-east-1.amazonaws.com")

EMAIL_HOST_PASSWORD = secrets.get("EMAIL_HOST_PASSWORD")

EMAIL_HOST_USER = secrets.get("EMAIL_HOST_USER")

EMAIL_PORT = 587

EMAIL_USE_TLS = True

FILE_CHARSET = "utf-8"

INTERNAL_IPS = ["127.0.0.1"]

LANGUAGE_CODE = "en-us"

MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"

ROOT_URLCONF = "terminusgps.urls"

SECRET_KEY = secrets.get("SECRET_KEY")

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = False

SERVER_EMAIL = "noreply@terminusgps.com"

SESSION_COOKIE_SECURE = True

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

SESSION_CACHE_ALIAS = "default"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = "/static/"

TIME_ZONE = "America/Chicago"

USE_I18N = True

USE_TZ = True

USE_X_FORWARDED_HOST = True

WAGTAIL_SITE_NAME = "Terminus GPS"

WAGTAILADMIN_BASE_URL = "https://app.terminusgps.com"

WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]

WAGTAILIMAGES_EXTENSIONS = ["avif", "gif", "jpg", "jpeg", "png", "webp", "svg"]

WIALON_TOKEN = secrets.get("WIALON_TOKEN")

WSGI_APPLICATION = "terminusgps.wsgi.application"

LOGGING_CONFIG = None
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "generic": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                "class": "logging.Formatter",
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "generic",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
        "loggers": {
            "django.request": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "authorizenet.sdk": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": True,
            },
            "gunicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "bucket_name": "media.terminusgps.com",
            "location": "uploads/",
            "region_name": "us-east-1",
            "verify": True,
            "custom_domain": secrets.get("AWS_CLOUDFRONT_CUSTOM_DOMAIN"),
            "cloudfront_key_id": secrets.get("AWS_CLOUDFRONT_KEY_ID"),
            "cloudfront_key": base64.b64decode(
                secrets.get("AWS_CLOUDFRONT_KEY")
            ),
            "querystring_auth": True,
            "endpoint_url": "https://s3.us-east-1.amazonaws.com",
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "bucket_name": "media.terminusgps.com",
            "location": "static/",
            "region_name": "us-east-1",
            "verify": True,
            "custom_domain": secrets.get("AWS_CLOUDFRONT_CUSTOM_DOMAIN"),
            "querystring_auth": False,
            "endpoint_url": "https://s3.us-east-1.amazonaws.com",
        },
    },
}

TASKS = {
    "default": {
        "BACKEND": "django_tasks_redis.RedisTaskBackend",
        "QUEUES": ["default"],
        "OPTIONS": {"REDIS_URL": "redis://127.0.0.1:6379/1"},
    }
}

INSTALLED_APPS = [
    "home.apps.HomeConfig",
    "docs",
    "django_tasks_redis",
    "corsheaders",
    "storages",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django.forms",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
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
                "wagtail.contrib.settings.context_processors.settings",
            ]
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": secrets.get("DB_NAME"),
        "HOST": secrets.get("DB_HOST"),
        "USER": secrets.get("DB_USERNAME"),
        "PASSWORD": secrets.get("DB_PASSWORD"),
        "PORT": secrets.get("DB_PORT", 5432),
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
