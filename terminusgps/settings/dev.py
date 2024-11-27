import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CORS_ORIGIN_ALLOW_ALL = True
DEBUG = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ENCRYPTION_KEY = "HX2qfcgHEtzd0UWUgDFUMKOeTVq5u-6DYASldb057W4="
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]
LANGUAGE_CODE = "en-us"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
SECRET_KEY = "po=qc@jlt0e#h6c8xv96vr%v2l^ib=f9m0!m-@bv0cz25pm$-g"
SERIALIZATION_MODULES = {"json": "djmoney.serializers"}
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
TAILWIND_APP_NAME = "theme"
TIME_ZONE = "America/Chicago"
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_MESSAGING_SID = os.getenv("TWILIO_MESSAGING_SID")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
USE_I18N = True
USE_TZ = True
WIALON_API_TOKEN = os.getenv("WIALON_API_TOKEN")
WIALON_ADMIN_ID = 27881459

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
    "tailwind",
    "terminusgps_tracker.apps.TerminusgpsTrackerConfig",
    "theme",
    "djmoney",
    "oauth2_provider",
    "corsheaders",
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
    "corsheaders.middleware.CorsMiddleware",
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
