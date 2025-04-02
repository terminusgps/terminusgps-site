from django.urls import path

from . import views

urlpatterns = [
    path("", views.CustomerDashboardView.as_view(), name="dashboard"),
    path("login/", views.TrackerLoginView.as_view(), name="login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="logout"),
    path("privacy/", views.TrackerPrivacyPolicyView.as_view(), name="privacy"),
    path("register/", views.TrackerRegisterView.as_view(), name="register"),
    path("source/", views.TrackerSourceCodeView.as_view(), name="source code"),
    path("settings/", views.CustomerSettingsView.as_view(), name="settings"),
    path("tiers/", views.SubscriptionTierListView.as_view(), name="list tiers"),
    path("support/", views.CustomerSupportView.as_view(), name="support"),
    path("support/token/", views.ConnectTokenView.as_view(), name="connect token"),
    path("apps/", views.TrackerMobileAppView.as_view(), name="mobile apps"),
    path(
        "payments/", views.CustomerPaymentMethodListView.as_view(), name="list payments"
    ),
    path(
        "payments/create/",
        views.CustomerPaymentMethodCreateView.as_view(),
        name="create payment",
    ),
    path(
        "payments/<int:pk>/",
        views.CustomerPaymentMethodDetailView.as_view(),
        name="detail payment",
    ),
    path(
        "payments/<int:pk>/delete/",
        views.CustomerPaymentMethodDeleteView.as_view(),
        name="delete payment",
    ),
    path(
        "addresses/",
        views.CustomerShippingAddressListView.as_view(),
        name="list addresses",
    ),
    path(
        "addresses/create/",
        views.CustomerShippingAddressCreateView.as_view(),
        name="create address",
    ),
    path(
        "addresses/<int:pk>/",
        views.CustomerShippingAddressDetailView.as_view(),
        name="detail address",
    ),
    path(
        "addresses/<int:pk>/delete/",
        views.CustomerShippingAddressDeleteView.as_view(),
        name="delete address",
    ),
    path(
        "subscription/<int:pk>/cancel/",
        views.CustomerSubscriptionDeleteView.as_view(),
        name="cancel subscription",
    ),
    path(
        "subscription/<int:pk>/",
        views.CustomerSubscriptionDetailView.as_view(),
        name="detail subscription",
    ),
    path(
        "subscription/<int:pk>/update/",
        views.CustomerSubscriptionUpdateView.as_view(),
        name="update subscription",
    ),
    path(
        "subscription/<int:pk>/transactions/",
        views.CustomerSubscriptionTransactionsView.as_view(),
        name="subscription transactions",
    ),
    path("assets/", views.CustomerAssetListView.as_view(), name="list assets"),
    path(
        "assets/<int:pk>/", views.CustomerAssetDetailView.as_view(), name="detail asset"
    ),
    path(
        "assets/<int:pk>/delete/",
        views.CustomerAssetDeleteView.as_view(),
        name="delete asset",
    ),
    path(
        "assets/create/", views.CustomerAssetCreateView.as_view(), name="create asset"
    ),
]
