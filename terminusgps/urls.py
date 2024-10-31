from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import oauth2_provider.urls as oauth2_urls

from . import views

urlpatterns = [
    path("o/", include(oauth2_urls)),
    path("privacy/", views.TerminusPrivacyView.as_view(), name="privacy"),
    path("source/", views.TerminusSourceView.as_view(), name="source"),
    path("contact/", views.TerminusContactView.as_view(), name="contact"),
    path("about/", views.TerminusAboutView.as_view(), name="about"),
    path(
        "accounts/password-reset/",
        views.TerminusPasswordResetView.as_view(),
        name="password reset",
    ),
    path("accounts/login/", views.TerminusLoginView.as_view(), name="login"),
    path("accounts/logout/", views.TerminusLogoutView.as_view(), name="logout"),
    path("accounts/profile/", views.TerminusProfileView.as_view(), name="profile"),
    path(
        "accounts/register/", views.TerminusRegistrationView.as_view(), name="register"
    ),
    path(
        "accounts/register/help/",
        views.TerminusRegistrationHelpView.as_view(),
        name="help register",
    ),
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("", include("terminusgps_tracker.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
