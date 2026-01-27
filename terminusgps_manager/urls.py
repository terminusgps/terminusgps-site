import terminusgps_payments.models
from django.urls import path, reverse_lazy

from . import forms, views

app_name = "terminusgps_manager"
urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("units/", views.UnitsView.as_view(), name="units"),
    path(
        "subscriptions/", views.SubscriptionView.as_view(), name="subscription"
    ),
    path(
        "payment-profiles/create/",
        views.AuthorizenetProfileCreateView.as_view(
            model=terminusgps_payments.models.CustomerPaymentProfile,
            form_class=forms.PaymentProfileCreateForm,
            template_name="terminusgps_manager/payment_profiles/create.html",
            success_url=reverse_lazy(
                "terminusgps_manager:list payment profiles"
            ),
        ),
        name="create payment profiles",
    ),
    path(
        "payment-profiles/list/",
        views.AuthorizenetProfileListView.as_view(
            model=terminusgps_payments.models.CustomerPaymentProfile,
            template_name="terminusgps_manager/payment_profiles/list.html",
        ),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/delete/",
        views.AuthorizenetProfileDeleteView.as_view(
            model=terminusgps_payments.models.CustomerPaymentProfile,
            template_name="terminusgps_manager/payment_profiles/delete.html",
            success_url=reverse_lazy(
                "terminusgps_manager:delete payment profiles success"
            ),
        ),
        name="delete payment profiles",
    ),
    path(
        "payment-profiles/delete/success/",
        views.AuthorizenetProfileDeleteSuccessView.as_view(
            template_name="terminusgps_manager/payment_profiles/delete_success.html"
        ),
        name="delete payment profiles success",
    ),
    path(
        "address-profiles/create/",
        views.AuthorizenetProfileCreateView.as_view(
            model=terminusgps_payments.models.CustomerAddressProfile,
            form_class=forms.AddressProfileCreateForm,
            template_name="terminusgps_manager/address_profiles/create.html",
            success_url=reverse_lazy(
                "terminusgps_manager:list address profiles"
            ),
        ),
        name="create address profiles",
    ),
    path(
        "address-profiles/list/",
        views.AuthorizenetProfileListView.as_view(
            model=terminusgps_payments.models.CustomerAddressProfile,
            template_name="terminusgps_manager/address_profiles/list.html",
        ),
        name="list address profiles",
    ),
    path(
        "address-profiles/<int:pk>/delete/",
        views.AuthorizenetProfileDeleteView.as_view(
            model=terminusgps_payments.models.CustomerAddressProfile,
            template_name="terminusgps_manager/address_profiles/delete.html",
            success_url=reverse_lazy(
                "terminusgps_manager:delete address profiles success"
            ),
        ),
        name="delete address profiles",
    ),
    path(
        "address-profiles/delete/success/",
        views.AuthorizenetProfileDeleteSuccessView.as_view(
            template_name="terminusgps_manager/address_profiles/delete_success.html"
        ),
        name="delete address profiles success",
    ),
]
