from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.CustomerDashboardView.as_view(), name="dashboard"),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
    path("pricing/", views.SubscriptionPricingView.as_view(), name="pricing"),
    path("support/", views.CustomerSupportView.as_view(), name="support"),
    path("units/", views.CustomerWialonUnitsView.as_view(), name="units"),
    path(
        "units/list/",
        views.CustomerWialonUnitListView.as_view(),
        name="unit list",
    ),
    path(
        "units/create/",
        views.CustomerWialonUnitCreateView.as_view(),
        name="unit create",
    ),
    path(
        "units/<int:pk>/",
        views.CustomerWialonUnitDetailView.as_view(),
        name="unit detail",
    ),
    path(
        "transactions/",
        views.CustomerTransactionsView.as_view(),
        name="transactions",
    ),
    path(
        "transactions/list/",
        views.CustomerTransactionListView.as_view(),
        name="transaction list",
    ),
    path(
        "tiers/list/",
        views.SubscriptionTierListView.as_view(),
        name="tier list",
    ),
    path(
        "tiers/<int:pk>/",
        views.SubscriptionTierDetailView.as_view(),
        name="tier detail",
    ),
    path(
        "subscription/",
        views.CustomerSubscriptionView.as_view(),
        name="subscription",
    ),
    path(
        "subscription/details/",
        views.SubscriptionDetailView.as_view(),
        name="subscription detail",
    ),
    path(
        "subscription/new/",
        views.SubscriptionCreateView.as_view(),
        name="subscription create",
    ),
    path(
        "subscription/update/",
        views.SubscriptionUpdateView.as_view(),
        name="subscription update",
    ),
    path(
        "payments/list/",
        views.CustomerPaymentMethodListView.as_view(),
        name="payment list",
    ),
    path(
        "payments/new/",
        views.CustomerPaymentMethodCreateView.as_view(),
        name="payment create",
    ),
    path(
        "payments/<int:pk>/",
        views.CustomerPaymentMethodDetailView.as_view(),
        name="payment detail",
    ),
    path(
        "payments/<int:pk>/delete/",
        views.CustomerPaymentMethodDeleteView.as_view(),
        name="payment delete",
    ),
    path(
        "addresses/list/",
        views.CustomerShippingAddressListView.as_view(),
        name="address list",
    ),
    path(
        "addresses/new/",
        views.CustomerShippingAddressCreateView.as_view(),
        name="address create",
    ),
    path(
        "addresses/<int:pk>/",
        views.CustomerShippingAddressDetailView.as_view(),
        name="address detail",
    ),
    path(
        "addresses/<int:pk>/delete/",
        views.CustomerShippingAddressDeleteView.as_view(),
        name="address delete",
    ),
]
