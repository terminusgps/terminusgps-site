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
    path("forms/login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("forms/logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path(
        "forms/register/",
        views.TrackerRegistrationView.as_view(),
        name="tracker register",
    ),
    path(
        "forms/credit-card/",
        views.CreditCardUploadView.as_view(),
        name="upload credit card",
    ),
    path("forms/asset/", views.AssetUploadView.as_view(), name="upload asset"),
    path(
        "forms/subscription/",
        views.SubscriptionSelectView.as_view(),
        name="select subscription",
    ),
    path("search-address/", views.AddressDropdownView.as_view(), name="search address"),
]
