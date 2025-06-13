from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.CustomerDashboardView.as_view(), name="dashboard"),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
    path("support/", views.CustomerSupportView.as_view(), name="support"),
    path("units/", views.CustomerWialonUnitsView.as_view(), name="units"),
    path(
        "units/list/",
        views.CustomerWialonUnitListView.as_view(),
        name="unit list",
    ),
    path(
        "units/list/<int:unit_pk>/detail/",
        views.CustomerWialonUnitListDetailView.as_view(),
        name="unit list detail",
    ),
    path(
        "units/list/<int:unit_pk>/update/",
        views.CustomerWialonUnitListUpdateView.as_view(),
        name="unit list update",
    ),
    path(
        "units/list/<int:unit_pk>/delete/",
        views.CustomerWialonUnitListDeleteView.as_view(),
        name="unit list delete",
    ),
    path(
        "units/create/",
        views.CustomerWialonUnitCreateView.as_view(),
        name="unit create",
    ),
    path(
        "subscription/",
        views.CustomerSubscriptionView.as_view(),
        name="subscription",
    ),
    path(
        "subscription/<int:sub_pk>/",
        views.SubscriptionDetailView.as_view(),
        name="subscription detail",
    ),
    path(
        "subscription/new/",
        views.SubscriptionCreateView.as_view(),
        name="subscription create",
    ),
    path(
        "subscription/<int:sub_pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="subscription update",
    ),
    path(
        "subscription/<int:sub_pk>/cancel/",
        views.SubscriptionDeleteView.as_view(),
        name="subscription delete",
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
