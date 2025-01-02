from django.urls import path
from . import views

urlpatterns = [
    path("", views.TrackerLandingView.as_view(), name="tracker landing"),
    path("profile/", views.TrackerProfileView.as_view(), name="tracker profile"),
    path("about/", views.TrackerAboutView.as_view(), name="tracker about"),
    path("contact/", views.TrackerContactView.as_view(), name="tracker contact"),
    path("source/", views.TrackerSourceView.as_view(), name="tracker source"),
    path("privacy/", views.TrackerPrivacyView.as_view(), name="tracker privacy"),
    path("login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path("signup/", views.TrackerSignupView.as_view(), name="tracker signup"),
    path("report/", views.TrackerBugReportView.as_view(), name="bug report"),
    path("assets/table/", views.AssetListView.as_view(), name="asset table"),
    path("assets/new/", views.AssetCreationView.as_view(), name="asset create"),
    path("assets/<int:id>/edit/", views.AssetUpdateView.as_view(), name="asset update"),
    path(
        "assets/<int:id>/delete/",
        views.AssetDeletionView.as_view(),
        name="asset delete",
    ),
    path(
        "subscriptions/",
        views.TrackerSubscriptionOptionsView.as_view(),
        name="tracker subscriptions",
    ),
    path("remote/<int:id>/", views.AssetRemoteView.as_view(), name="asset remote"),
    path(
        "remote/<int:id>/execute/",
        views.CommandExecutionView.as_view(),
        name="execute command",
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
        views.TrackerSubscriptionUpdateView.as_view(),
        name="modify subscription",
    ),
    path(
        "profile/settings/",
        views.TrackerProfileSettingsView.as_view(),
        name="profile settings",
    ),
    path(
        "profile/shipping/new/",
        views.ShippingAddressCreateView.as_view(),
        name="create shipping",
    ),
    path(
        "profile/shipping/<int:pk>/",
        views.ShippingAddressDetailView.as_view(),
        name="detail shipping",
    ),
    path(
        "profile/shipping/<int:pk>/delete/",
        views.ShippingAddressDeleteView.as_view(),
        name="delete shipping",
    ),
    path(
        "profile/payments/new/",
        views.PaymentMethodCreateView.as_view(),
        name="create payment",
    ),
    path(
        "profile/payments/<int:pk>/",
        views.PaymentMethodDetailView.as_view(),
        name="detail payment",
    ),
    path(
        "profile/payments/<int:pk>/delete/",
        views.PaymentMethodDeleteView.as_view(),
        name="delete payment",
    ),
]
