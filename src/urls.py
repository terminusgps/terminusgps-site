from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path(
        "accounts/register/",
        views.TerminusgpsRegisterView.as_view(),
        name="register",
    ),
    path("", views.TerminusgpsHomeView.as_view(), name="home"),
    path("hosting/", views.TerminusgpsHostingView.as_view(), name="hosting"),
    path(
        "source/",
        views.TerminusgpsSourceCodeView.as_view(),
        name="source code",
    ),
    path("navbar/", views.TerminusgpsNavbarView.as_view(), name="navbar"),
    path("about/", views.TerminusgpsAboutView.as_view(), name="about"),
    path("contact/", views.TerminusgpsContactView.as_view(), name="contact"),
    path(
        "commercial-use/",
        views.TerminusgpsCommercialUseView.as_view(),
        name="commercial use",
    ),
    path(
        "individual-use/",
        views.TerminusgpsIndividualUseView.as_view(),
        name="individual use",
    ),
    path(
        "teen-safety/",
        views.TerminusgpsTeenSafetyView.as_view(),
        name="teen safety",
    ),
    path(
        "senior-safety/",
        views.TerminusgpsSeniorSafetyView.as_view(),
        name="senior safety",
    ),
    path(
        "privacy/",
        views.TerminusgpsPrivacyPolicyView.as_view(),
        name="privacy",
    ),
    path(
        "terms/",
        views.TerminusgpsTermsAndConditionsView.as_view(),
        name="terms",
    ),
    path(
        "faq/",
        views.TerminusgpsFrequentlyAskedQuestionsView.as_view(),
        name="faq",
    ),
    path("payments/", include("terminusgps_payments.urls")),
    path("notifications/", include("terminusgps_notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
