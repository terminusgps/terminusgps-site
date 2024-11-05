from django.urls import path

from . import views

urlpatterns = [
    path("", views.TrackerProfileView.as_view(), name="tracker profile"),
    path("about/", views.TrackerAboutView.as_view(), name="tracker about"),
    path("contact/", views.TrackerContactView.as_view(), name="tracker contact"),
    path("source/", views.TrackerSourceView.as_view(), name="tracker source"),
    path("privacy/", views.TrackerPrivacyView.as_view(), name="tracker privacy"),
    path(
        "subscriptions/",
        views.TrackerSubscriptionView.as_view(),
        name="tracker subscriptions",
    ),
    path(
        "profile/subscription/",
        views.TrackerProfileSubscriptionView.as_view(),
        name="tracker profile subscription",
    ),
    path(
        "profile/payments/",
        views.TrackerProfilePaymentsView.as_view(),
        name="tracker profile payments",
    ),
    path(
        "profile/assets/",
        views.TrackerProfileAssetsView.as_view(),
        name="tracker profile assets",
    ),
    path("forms/login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("forms/logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path(
        "forms/register/",
        views.TrackerRegistrationView.as_view(),
        name="tracker register",
    ),
]
