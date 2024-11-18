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
    path(
        "profile/assets/",
        views.TrackerProfileAssetView.as_view(),
        name="profile assets",
    ),
    path(
        "profile/assets/new/",
        views.TrackerProfileAssetCreationView.as_view(),
        name="profile create asset",
    ),
    path(
        "profile/assets/delete/<int:imei_number>/",
        views.TrackerProfileAssetDeletionView.as_view(),
        name="profile delete asset",
    ),
    path(
        "profile/assets/update/<int:imei_number>/",
        views.TrackerProfileAssetModificationView.as_view(),
        name="profile update asset",
    ),
    path(
        "profile/subscription/",
        views.TrackerProfileSubscriptionView.as_view(),
        name="profile subscription",
    ),
    path(
        "profile/subscription/new/",
        views.TrackerProfileSubscriptionCreationView.as_view(),
        name="profile create subscription",
    ),
    path(
        "profile/subscription/delete/<int:imei_number>/",
        views.TrackerProfileSubscriptionDeletionView.as_view(),
        name="profile delete subscription",
    ),
    path(
        "profile/payments/",
        views.TrackerProfilePaymentMethodView.as_view(),
        name="profile payments",
    ),
    path(
        "profile/payments/new/",
        views.TrackerProfilePaymentMethodCreationView.as_view(),
        name="profile create payment",
    ),
    path(
        "profile/payments/delete/<int:pk>/",
        views.TrackerProfilePaymentMethodDeletionView.as_view(),
        name="profile delete payment",
    ),
    path(
        "profile/notifications/",
        views.TrackerProfileNotificationView.as_view(),
        name="profile notifications",
    ),
    path(
        "profile/notifications/new/",
        views.TrackerProfileNotificationCreationView.as_view(),
        name="profile create notification",
    ),
    path(
        "profile/notifications/delete/<int:pk>/",
        views.TrackerProfileNotificationDeletionView.as_view(),
        name="profile delete notification",
    ),
    path(
        "profile/notifications/update/<int:pk>/",
        views.TrackerProfileNotificationModificationView.as_view(),
        name="profile update notification",
    ),
    path("test_template/", views.TestTemplateView.as_view(), name="test template"),
]
