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
    path("register/", views.TrackerRegistrationView.as_view(), name="tracker register"),
    path(
        "subscriptions/",
        views.TrackerSubscriptionView.as_view(),
        name="tracker subscriptions",
    ),
    path("profile/assets/", views.TrackerProfileAssetView.as_view(), name="assets"),
    path(
        "profile/assets/new/",
        views.TrackerProfileAssetCreationView.as_view(),
        name="create asset",
    ),
    path(
        "profile/assets/update/<int:id>/",
        views.TrackerProfileAssetDeletionView.as_view(),
        name="update asset",
    ),
    path(
        "profile/assets/delete/<int:id>/",
        views.TrackerProfileAssetDeletionView.as_view(),
        name="delete asset",
    ),
    path(
        "profile/subscription/",
        views.TrackerProfileSubscriptionView.as_view(),
        name="subscription",
    ),
    path(
        "profile/subscription/new/",
        views.TrackerProfileSubscriptionCreationView.as_view(),
        name="create subscription",
    ),
    path(
        "profile/subscription/update/<int:id>/",
        views.TrackerProfileSubscriptionDeletionView.as_view(),
        name="modify subscription",
    ),
    path(
        "profile/subscription/delete/",
        views.TrackerProfileSubscriptionDeletionView.as_view(),
        name="delete subscription",
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
        "profile/payments/delete/<int:id>/",
        views.TrackerProfilePaymentMethodDeletionView.as_view(),
        name="delete payment",
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
        "profile/notifications/update/<int:id>/",
        views.TrackerProfileNotificationModificationView.as_view(),
        name="update notification",
    ),
    path(
        "profile/notifications/delete/<int:id>/",
        views.TrackerProfileNotificationDeletionView.as_view(),
        name="delete notification",
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
        "profile/shipping/update/<int:id>/",
        views.TrackerProfileShippingAddressCreationView.as_view(),
        name="update shipping",
    ),
    path(
        "profile/shipping/delete/<int:id>/",
        views.TrackerProfileShippingAddressDeletionView.as_view(),
        name="delete shipping",
    ),
]
