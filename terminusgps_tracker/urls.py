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
    path("assets/new/", views.AssetCreateView.as_view(), name="asset create"),
    path("assets/<int:pk>/", views.AssetDetailView.as_view(), name="asset detail"),
    path(
        "assets/<int:pk>/update/", views.AssetUpdateView.as_view(), name="asset update"
    ),
    path(
        "assets/<int:pk>/delete/", views.AssetDeleteView.as_view(), name="asset delete"
    ),
    path(
        "assets/<int:pk>/remote/", views.AssetRemoteView.as_view(), name="asset remote"
    ),
    path(
        "assets/<int:pk>/remote/execute/",
        views.CommandExecutionView.as_view(),
        name="execute command",
    ),
    path(
        "subscriptions/",
        views.TrackerSubscriptionTierListView.as_view(),
        name="tracker subscriptions",
    ),
    path(
        "profile/subscription/",
        views.TrackerSubscriptionDetailView.as_view(),
        name="subscription detail",
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
