from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register_view, name="register"),
    path("", views.home_view, name="home"),
    path("navbar/", views.navbar_view, name="navbar"),
    path("about/", views.about_view, name="about"),
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("source-code/", views.source_code_view, name="source code"),
    path("contact/", views.contact_view, name="contact"),
    path("platform/", views.platform_view, name="platform"),
    path("features/", views.features_view, name="features"),
    path("faq/", views.faq_view, name="faq"),
    path("", include("terminusgps_manager.urls", namespace="manager")),
]
