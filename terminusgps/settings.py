import os
from pathlib import Path

from intuitlib.enums import Scopes

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ADMINS = [
    ("Blake", "blake@terminusgps.com"),
    ("Lili", "lili@terminusgps.com"),
]

SECRET_KEY = "django-insecure-*jz*vcf%7n!$ij5n6ef0snfpg_xvbkeb5##pswykn6n&q&v8&j"
DEBUG = True
CLIENT = {
    "NAME": "TerminusGPS",
    "TITLE": "TerminusGPS, LLC.",
    "COPYRIGHT": "© 2024 TerminusGPS, LLC. All rights reserved.",
    "ADDRESS": {
        "STREET": "17240 Huffmeister Road",
        "CITY": "Cypress",
        "STATE": "TX",
        "ZIP": 77429,
    },
    "PHONE": {
        "MAIN": "+18448634809",
        "OTHER": "+17139045262",
    },
    "EMAIL": {
        "MAIN": "contact@terminusgps.com",
        "SUPPORT": "support@terminusgps.com",
        "SALES": "sales@terminusgps.com",
        "NOREPLY": "no-reply@terminusgps.com",
    },
    "SOCIAL": {
        "FACEBOOK": "https://www.facebook.com/terminusgps",
        "INSTAGRAM": "https://www.instagram.com/terminusgps",
        "X": "https://www.x.com/terminusgps",
        "TIKTOK": "https://tiktok.com/@terminusgps",
    },
}
WIALON_API_ACCESS_TOKEN = os.environ.get("WIALON_API_ACCESS_TOKEN", None)

SQUAREUP = {
    "ACCESS_TOKEN": os.environ.get("SQUARE_ACCESS_TOKEN", ""),
    "APP_ID": os.environ.get("SQUARE_APP_ID", ""),
    "APP_SECRET": os.environ.get("SQUARE_APP_SECRET", ""),
}

QUICKBOOKS = {
    "CLIENT_ID": os.environ.get("QB_CLIENT_ID", ""),
    "CLIENT_SECRET": os.environ.get("QB_CLIENT_SECRET", ""),
    "ENVIRONMENT": "sandbox",
    "REDIRECT_URI": "http://localhost:8000/pay/auth/",
    "SCOPES": [
        Scopes.OPENID,
        Scopes.EMAIL,
        Scopes.PAYMENT,
        Scopes.PROFILE,
    ],
}

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "dforms.apps.DformsConfig",
    "payments.apps.PaymentsConfig",
    "django_browser_reload",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "tailwind",
    "theme",
]

TAILWIND_APP_NAME = "theme"

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "terminusgps.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "terminusgps.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "postgresql": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "testdb",
        "USER": "blake",
        "PASSWORD": "terminusgps",
        "HOST": "",
        "PORT": "",
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Chicago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
