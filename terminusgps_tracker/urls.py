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
        views.TrackerSubscriptionOptionsView.as_view(),
        name="tracker subscriptions",
    ),
    path(
        "profile/subscription/<int:tier>/confirm/",
        views.TrackerSubscriptionConfirmView.as_view(),
        name="confirm subscription",
    ),
    path(
        "profile/subscription/success/",
        views.TrackerSubscriptionSuccessView.as_view(),
        name="success subscription",
    ),
    path(
        "profile/subscription/<int:pk>/update/",
        views.TrackerProfileSubscriptionModificationView.as_view(),
        name="modify subscription",
    ),
    path(
        "profile/settings/",
        views.TrackerProfileSettingsView.as_view(),
        name="profile settings",
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
