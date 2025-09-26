from django.urls import path

from . import views

app_name = "terminusgps_tracker"

urlpatterns = [
    path(
        "dashboard/", views.CustomerDashboardView.as_view(), name="dashboard"
    ),
    path("units/", views.CustomerUnitsView.as_view(), name="units"),
    path("account/", views.CustomerAccountView.as_view(), name="account"),
    path(
        "subscription/",
        views.CustomerSubscriptionView.as_view(),
        name="subscription",
    ),
    path(
        "subscription/create/",
        views.CustomerSubscriptionCreateView.as_view(),
        name="create subscription",
    ),
    path(
        "units/list/",
        views.CustomerWialonUnitListView.as_view(),
        name="list unit",
    ),
    path(
        "units/create/",
        views.CustomerWialonUnitCreateView.as_view(),
        name="create unit",
    ),
    path(
        "units/<int:unit_pk>/detail/",
        views.CustomerWialonUnitDetailView.as_view(),
        name="detail unit",
    ),
    path(
        "units/<int:unit_pk>/update/",
        views.CustomerWialonUnitUpdateView.as_view(),
        name="update unit",
    ),
    path(
        "units/<int:unit_pk>/delete/",
        views.CustomerWialonUnitDeleteView.as_view(),
        name="delete unit",
    ),
]
