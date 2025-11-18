from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("navbar/", views.NavbarView.as_view(), name="navbar"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("hosting/", views.HostingView.as_view(), name="hosting"),
    path("source/", views.SourceCodeView.as_view(), name="source code"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path(
        "commercial-use/",
        views.CommercialUseView.as_view(),
        name="commercial use",
    ),
    path(
        "individual-use/",
        views.IndividualUseView.as_view(),
        name="individual use",
    ),
    path("teen-safety/", views.TeenSafetyView.as_view(), name="teen safety"),
    path(
        "senior-safety/",
        views.SeniorSafetyView.as_view(),
        name="senior safety",
    ),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", views.TermsAndConditionsView.as_view(), name="terms"),
    path("faq/", views.FrequentlyAskedQuestionsView.as_view(), name="faq"),
    path("django-rq/", include("django_rq.urls")),
    path("payments/", include("terminusgps_payments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
