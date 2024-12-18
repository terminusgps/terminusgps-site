from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("docs/", include("docs.urls")),
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path(
        "register/", views.TerminusRegistrationView.as_view(), name="terminus register"
    ),
    path("", include("terminusgps_tracker.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
