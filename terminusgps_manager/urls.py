from django.urls import path

from . import views

app_name = "terminusgps_manager"
urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("units/", views.UnitsView.as_view(), name="units"),
    path(
        "subscriptions/", views.SubscriptionView.as_view(), name="subscription"
    ),
    path(
        "subscriptions/create/",
        views.SubscriptionCreateView.as_view(),
        name="create subscriptions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/transactions/",
        views.SubscriptionTransactionsView.as_view(),
        name="subscription transactions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/detail/",
        views.SubscriptionDetailView.as_view(),
        name="detail subscriptions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/delete/",
        views.SubscriptionDeleteView.as_view(),
        name="delete subscriptions",
    ),
    path(
        "subscriptions/<int:subscription_pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="update subscriptions",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/create/",
        views.CustomerPaymentProfileCreateView.as_view(),
        name="create payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/list/",
        views.CustomerPaymentProfileListView.as_view(),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/<int:paymentprofile_pk>/detail/",
        views.CustomerPaymentProfileDetailView.as_view(),
        name="detail payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/<int:paymentprofile_pk>/delete/",
        views.CustomerPaymentProfileDeleteView.as_view(),
        name="delete payment profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/create/",
        views.CustomerAddressProfileCreateView.as_view(),
        name="create address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/list/",
        views.CustomerAddressProfileListView.as_view(),
        name="list address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/<int:addressprofile_pk>/detail/",
        views.CustomerAddressProfileDetailView.as_view(),
        name="detail address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/<int:addressprofile_pk>/delete/",
        views.CustomerAddressProfileDeleteView.as_view(),
        name="delete address profiles",
    ),
]
