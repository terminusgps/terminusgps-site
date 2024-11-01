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
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("", include("terminusgps_tracker.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
