from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.CustomerDashboardView.as_view(), name="dashboard"),
    path("pricing/", views.SubscriptionPricingView.as_view(), name="pricing"),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
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
        "payments/",
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
        "addresses/",
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
]
