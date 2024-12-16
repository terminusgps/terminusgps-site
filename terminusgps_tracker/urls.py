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
        "profile/settings/",
        views.TrackerProfileSettingsView.as_view(),
        name="profile settings",
    ),
    path("profile/assets/", views.TrackerProfileAssetView.as_view(), name="assets"),
    path(
        "profile/assets/new/",
        views.TrackerProfileAssetCreationView.as_view(),
        name="create asset",
    ),
    path(
        "profile/assets/<int:id>/update/",
        views.TrackerProfileAssetModificationView.as_view(),
        name="update asset",
    ),
    path(
        "profile/shipping/",
        views.TrackerProfileShippingAddressView.as_view(),
        name="shipping",
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
        "profile/shipping/<int:id>/set-default/",
        views.TrackerProfileShippingAddressSetDefaultView.as_view(),
        name="default shipping",
    ),
    path(
        "profile/subscription/",
        views.TrackerProfileSubscriptionView.as_view(),
        name="subscription",
    ),
    path(
        "profile/subscription/<int:id>/update/",
        views.TrackerProfileSubscriptionView.as_view(),
        name="modify subscription",
    ),
    path(
        "profile/payments/",
        views.TrackerProfilePaymentMethodView.as_view(),
        name="payments",
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
    path(
        "profile/payments/<int:id>/set-default/",
        views.TrackerProfilePaymentMethodSetDefaultView.as_view(),
        name="default payment",
    ),
    path(
        "profile/notifications/",
        views.TrackerProfileNotificationView.as_view(),
        name="notifications",
    ),
    path(
        "profile/notifications/new/",
        views.TrackerProfileNotificationCreationView.as_view(),
        name="create notification",
    ),
    path(
        "profile/notifications/<int:id>/update/",
        views.TrackerProfileNotificationModificationView.as_view(),
        name="update notification",
    ),
    path(
        "profile/notifications/<int:id>/delete/",
        views.TrackerProfileNotificationDeletionView.as_view(),
        name="delete notification",
    ),
]
