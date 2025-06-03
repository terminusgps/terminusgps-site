from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.CustomerDashboardView.as_view(), name="dashboard"),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
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
