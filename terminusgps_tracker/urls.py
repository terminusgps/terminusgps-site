from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.CustomerDashboardView.as_view(), name="dashboard"),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
    path("units/", views.CustomerWialonUnitsView.as_view(), name="units"),
    path(
        "units/<int:customer_pk>/list/",
        views.CustomerWialonUnitListView.as_view(),
        name="unit list",
    ),
    path(
        "units/<int:customer_pk>/list/<int:unit_pk>/detail/",
        views.CustomerWialonUnitListDetailView.as_view(),
        name="unit list detail",
    ),
    path(
        "units/<int:customer_pk>/list/<int:unit_pk>/update/",
        views.CustomerWialonUnitListUpdateView.as_view(),
        name="unit list update",
    ),
    path(
        "units/<int:customer_pk>/create/",
        views.CustomerWialonUnitCreateView.as_view(),
        name="unit create",
    ),
    path(
        "subscription/",
        views.CustomerSubscriptionView.as_view(),
        name="subscription",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/",
        views.SubscriptionDetailView.as_view(),
        name="subscription detail",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/items/",
        views.SubscriptionItemListView.as_view(),
        name="subscription items",
    ),
    path(
        "subscription/<int:customer_pk>/new/",
        views.SubscriptionCreateView.as_view(),
        name="subscription create",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="subscription update",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/cancel/",
        views.SubscriptionDeleteView.as_view(),
        name="subscription delete",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/transactions/",
        views.SubscriptionTransactionsView.as_view(),
        name="subscription transactions",
    ),
    path(
        "transactions/<int:transaction_id>/",
        views.SubscriptionTransactionDetailView.as_view(),
        name="transaction detail",
    ),
    path(
        "payments/<int:customer_pk>/new/",
        views.CustomerPaymentMethodCreateView.as_view(),
        name="payment create",
    ),
    path(
        "payments/<int:customer_pk>/<int:payment_pk>/",
        views.CustomerPaymentMethodDetailView.as_view(),
        name="payment detail",
    ),
    path(
        "payments/<int:customer_pk>/<int:payment_pk>/delete/",
        views.CustomerPaymentMethodDeleteView.as_view(),
        name="payment delete",
    ),
    path(
        "payments/<int:customer_pk>/list/",
        views.CustomerPaymentMethodListView.as_view(),
        name="payment list",
    ),
    path(
        "payments/<int:customer_pk>/choices/",
        views.CustomerPaymentMethodChoicesView.as_view(),
        name="payment choices",
    ),
    path(
        "addresses/<int:customer_pk>/new/",
        views.CustomerShippingAddressCreateView.as_view(),
        name="address create",
    ),
    path(
        "addresses/<int:customer_pk>/<int:address_pk>/",
        views.CustomerShippingAddressDetailView.as_view(),
        name="address detail",
    ),
    path(
        "addresses/<int:customer_pk>/<int:address_pk>/delete/",
        views.CustomerShippingAddressDeleteView.as_view(),
        name="address delete",
    ),
    path(
        "addresses/<int:customer_pk>/list/",
        views.CustomerShippingAddressListView.as_view(),
        name="address list",
    ),
    path(
        "addresses/<int:customer_pk>/choices/",
        views.CustomerShippingAddressChoicesView.as_view(),
        name="address choices",
    ),
]
