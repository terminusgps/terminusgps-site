from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("source-code/", views.source_code_view, name="source code"),
    path("contact/", views.contact_view, name="contact"),
    path("platform/", views.platform_view, name="platform"),
    path("cameras/", views.cameras_view, name="cameras"),
    path("features/", views.features_view, name="features"),
    path("faq/", views.faq_view, name="faq"),
    path("apps/ios/", views.ios_app_view, name="ios app"),
    path("apps/android/", views.android_app_view, name="android app"),
    path("contact/form/", views.contact_form_view, name="contact form"),
    path(
        "contact/form/success/",
        views.contact_form_success_view,
        name="contact form success",
    ),
]
