from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path(
        "register/", views.TerminusgpsRegisterView.as_view(), name="register"
    ),
    path("login/", views.TerminusgpsLoginView.as_view(), name="login"),
    path("logout/", views.TerminusgpsLogoutView.as_view(), name="logout"),
    path(
        "reset-password/",
        views.TerminusgpsPasswordResetView.as_view(),
        name="password reset",
    ),
    path(
        "reset-password/done/",
        views.TerminusgpsPasswordResetDoneView.as_view(),
        name="password reset done",
    ),
    path(
        "reset-password/<str:uidb64>/<str:token>/confirm/",
        views.TerminusgpsPasswordResetConfirmView.as_view(),
        name="password reset confirm",
    ),
    path(
        "reset-password/complete/",
        views.TerminusgpsPasswordResetCompleteView.as_view(),
        name="password reset complete",
    ),
    path(
        "privacy/",
        views.TerminusgpsPrivacyPolicyView.as_view(),
        name="privacy",
    ),
    path(
        "apps/", views.TerminusgpsMobileAppView.as_view(), name="mobile apps"
    ),
    path(
        "source/",
        views.TerminusgpsSourceCodeView.as_view(),
        name="source code",
    ),
    path("hosting/", views.TerminusgpsHostingView.as_view(), name="hosting"),
    path("about/", views.TerminusgpsAboutView.as_view(), name="about"),
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
    path("contact/", views.TerminusgpsContactView.as_view(), name="contact"),
    path("", views.TerminusgpsHomepageView.as_view(), name="home"),
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
