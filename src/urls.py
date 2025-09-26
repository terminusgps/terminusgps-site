from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import cache_page

from . import views

cached = lambda view_func: cache_page(timeout=60 * 15)(view_func)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path(
        "accounts/register/",
        views.TerminusgpsRegisterView.as_view(),
        name="register",
    ),
    path("", cached(views.TerminusgpsHomeView.as_view()), name="home"),
    path("hosting/", views.TerminusgpsHostingView.as_view(), name="hosting"),
    path(
        "source/",
        views.TerminusgpsSourceCodeView.as_view(),
        name="source code",
    ),
    path("about/", cached(views.TerminusgpsAboutView.as_view()), name="about"),
    path(
        "contact/",
        cached(views.TerminusgpsContactView.as_view()),
        name="contact",
    ),
    path(
        "commercial-use/",
        cached(views.TerminusgpsCommercialUseView.as_view()),
        name="commercial use",
    ),
    path(
        "individual-use/",
        cached(views.TerminusgpsIndividualUseView.as_view()),
        name="individual use",
    ),
    path(
        "teen-safety/",
        cached(views.TerminusgpsTeenSafetyView.as_view()),
        name="teen safety",
    ),
    path(
        "senior-safety/",
        cached(views.TerminusgpsSeniorSafetyView.as_view()),
        name="senior safety",
    ),
    path(
        "privacy/",
        cached(views.TerminusgpsPrivacyPolicyView.as_view()),
        name="privacy",
    ),
    path(
        "terms/",
        cached(views.TerminusgpsTermsAndConditionsView.as_view()),
        name="terms",
    ),
    path(
        "faq/",
        cached(views.TerminusgpsFrequentlyAskedQuestionsView.as_view()),
        name="faq",
    ),
    path("payments/", include("terminusgps_payments.urls")),
    path("", include("terminusgps_tracker.urls", namespace="tracker")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
