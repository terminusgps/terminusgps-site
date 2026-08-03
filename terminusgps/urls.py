from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path(
        "jsi18n/",
        cache_page(3600)(JavaScriptCatalog.as_view(packages=["formset"])),
        name="javascript-catalog",
    ),
    path("", include("terminusgps_site.urls")),
    path(
        "install/",
        include("terminusgps_installer.urls", namespace="installer"),
    ),
]
