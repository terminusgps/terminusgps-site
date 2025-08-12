from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

cached = lambda view_func: cache_page(timeout=60 * 15)(view_func)
app_name = "tracker"

urlpatterns = [
    path(
        "dashboard/", views.CustomerDashboardView.as_view(), name="dashboard"
    ),
    path(
        "subscription/",
        views.CustomerSubscriptionView.as_view(),
        name="subscription",
    ),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
    path("units/", views.CustomerWialonUnitsView.as_view(), name="units"),
    path(
        "units/<int:customer_pk>/list/",
        views.CustomerWialonUnitListView.as_view(),
        name="unit list",
    ),
    path(
        "units/<int:customer_pk>/list/<int:unit_pk>/detail/",
        cached(views.CustomerWialonUnitListDetailView.as_view()),
        name="unit list detail",
    ),
    path(
        "units/<int:customer_pk>/list/<int:unit_pk>/update/",
        views.CustomerWialonUnitListUpdateView.as_view(),
        name="unit list update",
    ),
    path(
        "units/<int:customer_pk>/create/",
        cached(views.CustomerWialonUnitCreateView.as_view()),
        name="unit create",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/",
        views.SubscriptionDetailView.as_view(),
        name="subscription detail",
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
        cached(views.SubscriptionDeleteView.as_view()),
        name="subscription delete",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/transactions/",
        views.SubscriptionTransactionsView.as_view(),
        name="subscription transactions",
    ),
    path(
        "subscription/<int:customer_pk>/<int:sub_pk>/items/",
        views.SubscriptionItemListView.as_view(),
        name="subscription items",
    ),
    path(
        "transactions/<int:transaction_id>/",
        cached(views.SubscriptionTransactionDetailView.as_view()),
        name="transaction detail",
    ),
    path(
        "payments/<int:customer_pk>/new/",
        cached(views.CustomerPaymentMethodCreateView.as_view()),
        name="payment create",
    ),
    path(
        "payments/<int:customer_pk>/<int:payment_pk>/",
        cached(views.CustomerPaymentMethodDetailView.as_view()),
        name="payment detail",
    ),
    path(
        "payments/<int:customer_pk>/<int:payment_pk>/delete/",
        cached(views.CustomerPaymentMethodDeleteView.as_view()),
        name="payment delete",
    ),
    path(
        "payments/<int:customer_pk>/list/",
        views.CustomerPaymentMethodListView.as_view(),
        name="payment list",
    ),
    path(
        "addresses/<int:customer_pk>/new/",
        cached(views.CustomerShippingAddressCreateView.as_view()),
        name="address create",
    ),
    path(
        "addresses/<int:customer_pk>/<int:address_pk>/",
        cached(views.CustomerShippingAddressDetailView.as_view()),
        name="address detail",
    ),
    path(
        "addresses/<int:customer_pk>/<int:address_pk>/delete/",
        cached(views.CustomerShippingAddressDeleteView.as_view()),
        name="address delete",
    ),
    path(
        "addresses/<int:customer_pk>/list/",
        views.CustomerShippingAddressListView.as_view(),
        name="address list",
    ),
]
