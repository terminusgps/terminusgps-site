from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("docs/", include("docs.urls")),
    path("about/", views.TerminusgpsAboutView.as_view(), name="about"),
    path("contact/", views.TerminusgpsContactView.as_view(), name="contact"),
    path("hosting/", views.TerminusgpsHostingView.as_view(), name="hosting"),
    path("login/", views.TerminusgpsLoginView.as_view(), name="login"),
    path("logout/", views.TerminusgpsLogoutView.as_view(), name="logout"),
    path("", views.TerminusgpsHomeView.as_view(), name="home"),
    path(
        "safety/teens/",
        views.TerminusgpsTeenSafetyView.as_view(),
        name="teen safety",
    ),
    path(
        "safety/seniors/",
        views.TerminusgpsSeniorSafetyView.as_view(),
        name="senior safety",
    ),
    path("", views.TerminusgpsHomeView.as_view(), name="home"),
    path(
        "register/", views.TerminusgpsRegisterView.as_view(), name="register"
    ),
    path(
        "safety/teens/",
        views.TerminusgpsTeenSafetyView.as_view(),
        name="teen safety",
    ),
    path(
        "safety/seniors/",
        views.TerminusgpsSeniorSafetyView.as_view(),
        name="senior safety",
    ),
    path(
        "privacy/",
        views.TerminusgpsPrivacyPolicyView.as_view(),
        name="privacy",
    ),
    path(
        "source/",
        views.TerminusgpsSourceCodeView.as_view(),
        name="source code",
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
    path(
        "install/",
        include("terminusgps_installer.urls", namespace="installer"),
    ),
    path("", include("terminusgps_tracker.urls", namespace="tracker")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
