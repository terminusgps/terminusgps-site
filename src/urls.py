from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("platform/", views.PlatformView.as_view(), name="platform"),
    path("source/", views.SourceCodeView.as_view(), name="source code"),
    path("features/", views.FeaturesView.as_view(), name="features"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", views.TermsAndConditionsView.as_view(), name="terms"),
    path("faq/", views.FrequentlyAskedQuestionsView.as_view(), name="faq"),
    path("apps/ios/", views.IOSAppView.as_view(), name="ios app"),
    path("apps/android/", views.AndroidAppView.as_view(), name="android app"),
    path("teen-safety/", views.TeenSafetyView.as_view(), name="teen safety"),
    path(
        "senior-safety/",
        views.SeniorSafetyView.as_view(),
        name="senior safety",
    ),
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
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "password-change/",
        views.PasswordChangeView.as_view(),
        name="password change",
    ),
    path(
        "password-change/success/",
        views.PasswordChangeSuccessView.as_view(),
        name="password change success",
    ),
    path(
        "password-reset/",
        views.PasswordResetView.as_view(),
        name="password reset",
    ),
    path(
        "password-reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password reset done",
    ),
    path(
        "password-reset/<uidb64>/<token>/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password reset confirm",
    ),
    path(
        "password-reset/complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password reset complete",
    ),
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
