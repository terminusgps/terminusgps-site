from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "platform/",
        views.PermanentRedirectView.as_view(
            url="https://hosting.terminusgps.com/", query_string=True
        ),
        name="platform",
    ),
    path(
        "source/",
        views.PermanentRedirectView.as_view(
            url="https://github.com/terminusgps/terminusgps-site/"
        ),
        name="source code",
    ),
    path(
        "apps/ios/",
        views.PermanentRedirectView.as_view(
            url="https://apps.apple.com/us/app/terminus-gps-mobile/id1419439009"
        ),
        name="ios app",
    ),
    path(
        "apps/android/",
        views.PermanentRedirectView.as_view(
            url="https://play.google.com/store/apps/details?id=com.terminusgps.track&pcampaignid=web_share"
        ),
        name="android app",
    ),
    path(
        "",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/home.html",
            extra_context={
                "title": "Home",
                "subtitle": "In God we trust, all others we track",
            },
        ),
        name="home",
    ),
    path(
        "features/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/features.html",
            extra_context={
                "title": "Features",
                "subtitle": "Your entire fleet, at your fingertips",
            },
        ),
        name="features",
    ),
    path(
        "about/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/about.html",
            extra_context={
                "title": "About",
                "subtitle": "Why we do what we do",
            },
        ),
        name="about",
    ),
    path(
        "contact/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/contact.html",
            extra_context={"title": "Contact", "subtitle": "Drop us a line"},
        ),
        name="contact",
    ),
    path(
        "privacy/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/privacy.html",
            extra_context={
                "title": "Privacy Policy",
                "subtitle": "How we use your data",
            },
        ),
        name="privacy",
    ),
    path(
        "terms/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/terms.html",
            extra_context={
                "title": "Terms & Conditions",
                "subtitle": "You agree to these by using Terminus GPS services",
            },
        ),
        name="terms",
    ),
    path(
        "faq/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/faq.html",
            extra_context={
                "title": "Frequently Asked Questions",
                "subtitle": "With frequently cited answers",
            },
        ),
        name="faq",
    ),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        views.HtmxTemplateView.as_view(
            template_name="terminusgps/logout.html",
            extra_context={"title": "Logout"},
        ),
        name="logout",
    ),
    path("logged_out/", views.LogoutView.as_view(), name="logged out"),
    path("", include("terminusgps_manager.urls")),
]

if not settings.DEBUG:
    urlpatterns.insert(-2, path("django-rq/", include("django_rq.urls")))
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
