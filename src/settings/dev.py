import os
from pathlib import Path

os.umask(0)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CORS_ORIGIN_ALLOW_ALL = True
DEBUG = True
DOCS_ACCESS = "staff"
DOCS_ROOT = BASE_DIR.parent / "docs/build/html"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FROM_EMAIL = "no-reply@terminusgps.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
TAILWIND_APP_NAME = "theme"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True

SECRET_KEY = os.getenv("SECRET_KEY")
CONNECT_SECRET = os.getenv("CONNECT_SECRET")
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_MESSAGING_SID = os.getenv("TWILIO_MESSAGING_SID")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
WIALON_TOKEN = os.getenv("WIALON_TOKEN")
WIALON_HOST = os.getenv("WIALON_HOST")
WIALON_ADMIN_ID = os.getenv("WIALON_ADMIN_ID")
WIALON_UNACTIVATED_GROUP = os.getenv("WIALON_UNACTIVATED_GROUP")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


TRACKER_PROFILE = {
    "DISPLAY_NAME": "Terminus GPS",
    "GITHUB": "https://github.com/terminusgps/terminusgps-site/",
    "MOTD": "Check out the Terminus GPS mobile app!",
    "LEGAL_NAME": "Terminus GPS, LLC",
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
    ],
    "SUBSCRIPTIONS": [
        {"NAME": "Basic", "OPTIONS": {"cmd": "Basic", "amount": "19.99"}},
        {"NAME": "Standard", "OPTIONS": {"cmd": "Standard", "amount": "29.99"}},
        {"NAME": "Premium", "OPTIONS": {"cmd": "Premium", "amount": "39.99"}},
    ],
}


STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
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
    "django_browser_reload",
    "django_htmx",
    "docs",
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
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "src.urls"

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
