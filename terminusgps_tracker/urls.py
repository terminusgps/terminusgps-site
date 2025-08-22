from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

cached = lambda view_func: cache_page(timeout=60 * 15)(view_func)
app_name = "tracker"

urlpatterns = [
    path(
        "dashboard/", views.CustomerDashboardView.as_view(), name="dashboard"
    ),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
    path(
        "subscription/",
        views.CustomerSubscriptionView.as_view(),
        name="subscription",
    ),
    path("units/", views.CustomerUnitsView.as_view(), name="units"),
    path("todo/", views.CustomerTodoView.as_view(), name="todo"),
    path(
        "subscriptions/create/",
        views.CustomerSubscriptionCreateView.as_view(),
        name="create subscription",
    ),
    path(
        "subscriptions/detail/<int:customer_pk>/<int:subcription_pk>/",
        views.CustomerSubscriptionDetailView.as_view(),
        name="detail subscription",
    ),
    path(
        "subscriptions/update/<int:customer_pk>/<int:subcription_pk>/",
        views.CustomerSubscriptionUpdateView.as_view(),
        name="update subscription",
    ),
    path(
        "subscriptions/delete/<int:customer_pk>/<int:subcription_pk>/",
        views.CustomerSubscriptionDeleteView.as_view(),
        name="delete subscription",
    ),
    path(
        "payments/create/",
        cached(views.CustomerPaymentMethodCreateView.as_view()),
        name="create payment",
    ),
    path(
        "payments/detail/<int:customer_pk>/<int:payment_pk>/",
        cached(views.CustomerPaymentMethodDetailView.as_view()),
        name="detail payment",
    ),
    path(
        "payments/list/<int:customer_pk>/",
        views.CustomerPaymentMethodListView.as_view(),
        name="list payment",
    ),
    path(
        "payments/delete/<int:customer_pk>/<int:payment_pk>/",
        cached(views.CustomerPaymentMethodDeleteView.as_view()),
        name="delete payment",
    ),
    path(
        "addresses/create/",
        cached(views.CustomerShippingAddressCreateView.as_view()),
        name="create address",
    ),
    path(
        "addresses/detail/<int:customer_pk>/<int:address_pk>/",
        cached(views.CustomerShippingAddressDetailView.as_view()),
        name="detail address",
    ),
    path(
        "addresses/list/<int:customer_pk>/",
        views.CustomerShippingAddressListView.as_view(),
        name="list address",
    ),
    path(
        "addresses/delete/<int:customer_pk>/<int:address_pk>/",
        cached(views.CustomerShippingAddressDeleteView.as_view()),
        name="delete address",
    ),
    path(
        "units/create/",
        cached(views.CustomerWialonUnitCreateView.as_view()),
        name="create unit",
    ),
    path(
        "units/detail/<int:customer_pk>/<int:unit_pk>/",
        views.CustomerWialonUnitDetailView.as_view(),
        name="detail unit",
    ),
    path(
        "units/list/<int:customer_pk>/",
        views.CustomerWialonUnitListView.as_view(),
        name="list unit",
    ),
    path(
        "units/update/<int:customer_pk>/<int:unit_pk>/",
        views.CustomerWialonUnitUpdateView.as_view(),
        name="update unit",
    ),
]
