from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.TrackerProfileView.as_view(), name="tracker profile"),
    path("about/", views.TrackerAboutView.as_view(), name="tracker about"),
    path("contact/", views.TrackerContactView.as_view(), name="tracker contact"),
    path("source/", views.TrackerSourceView.as_view(), name="tracker source"),
    path("privacy/", views.TrackerPrivacyView.as_view(), name="tracker privacy"),
    path("login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path("signup/", views.TrackerSignupView.as_view(), name="tracker signup"),
    path(
        "subscriptions/",
        views.TrackerSubscriptionView.as_view(),
        name="tracker subscriptions",
    ),
    path(
        "subscriptions/<int:pk>/",
        views.TrackerSubscriptionTierDetailView.as_view(),
        name="tier detail",
    ),
    path(
        "profile/settings/",
        views.TrackerProfileSettingsView.as_view(),
        name="profile settings",
    ),
    path(
        "profile/assets/new/",
        views.TrackerProfileAssetCreationView.as_view(),
        name="create asset",
    ),
    path(
        "profile/shipping/new/",
        views.TrackerProfileShippingAddressCreationView.as_view(),
        name="create shipping",
    ),
    path(
        "profile/shipping/<int:id>/delete/",
        views.TrackerProfileShippingAddressDeletionView.as_view(),
        name="delete shipping",
    ),
    path(
        "profile/subscription/<int:id>/update/<int:tier>/",
        views.TrackerProfileSubscriptionUpdateView.as_view(),
        name="update subscription",
    ),
    path(
        "profile/payments/new/",
        views.TrackerProfilePaymentMethodCreationView.as_view(),
        name="create payment",
    ),
    path(
        "profile/payments/<int:id>/delete/",
        views.TrackerProfilePaymentMethodDeletionView.as_view(),
        name="delete payment",
    ),
]
