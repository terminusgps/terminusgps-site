from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

cached = lambda view_func: cache_page(timeout=60 * 15)(view_func)
app_name = "tracker"

urlpatterns = [
    path(
        "subscriptions/<int:customer_pk>/<int:subcription_pk>/",
        views.CustomerSubscriptionDetailView.as_view(),
        name="detail subscription",
    ),
    path(
        "subscriptions/<int:customer_pk>/<int:subcription_pk>/delete/",
        views.CustomerSubscriptionDeleteView.as_view(),
        name="delete subscription",
    ),
    path(
        "subscriptions/<int:customer_pk>/<int:subcription_pk>/update/",
        views.CustomerSubscriptionUpdateView.as_view(),
        name="update subscription",
    ),
    path(
        "subscriptions/<int:customer_pk>/create/",
        views.CustomerSubscriptionCreateView.as_view(),
        name="create subscription",
    ),
    path(
        "payments/<int:customer_pk>/",
        views.CustomerPaymentMethodCreateView.as_view(),
        name="create payment",
    ),
    path(
        "payments/<int:customer_pk>/<int:payment_pk>/",
        views.CustomerPaymentMethodDetailView.as_view(),
        name="detail payment",
    ),
    path(
        "payments/<int:customer_pk>/list/",
        views.CustomerPaymentMethodListView.as_view(),
        name="list payment",
    ),
    path(
        "payments/<int:customer_pk>/<int:payment_pk>/delete/",
        views.CustomerPaymentMethodDeleteView.as_view(),
        name="delete payment",
    ),
    path(
        "addresses/<int:customer_pk>/",
        views.CustomerShippingAddressCreateView.as_view(),
        name="create address",
    ),
    path(
        "addresses/<int:customer_pk>/<int:address_pk>/",
        views.CustomerShippingAddressDetailView.as_view(),
        name="detail address",
    ),
    path(
        "addresses/<int:customer_pk>/list/",
        views.CustomerShippingAddressListView.as_view(),
        name="list address",
    ),
    path(
        "addresses/<int:customer_pk>/<int:address_pk>/delete/",
        views.CustomerShippingAddressDeleteView.as_view(),
        name="delete address",
    ),
    path(
        "units/<int:customer_pk>/create/",
        views.CustomerWialonUnitCreateView.as_view(),
        name="create unit",
    ),
    path(
        "units/<int:customer_pk>/<int:unit_pk>/",
        views.CustomerWialonUnitDetailView.as_view(),
        name="detail unit",
    ),
    path(
        "units/<int:customer_pk>/list/",
        views.CustomerWialonUnitListView.as_view(),
        name="list unit",
    ),
    path(
        "units/<int:customer_pk>/<int:unit_pk>/update/",
        views.CustomerWialonUnitUpdateView.as_view(),
        name="update unit",
    ),
]
