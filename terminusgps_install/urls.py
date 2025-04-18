from django.urls import path

from . import views

app_name = "install"
urlpatterns = [
    path("", views.InstallDashboardView.as_view(), name="dashboard"),
    path("scan-vin/", views.InstallScanVinNumberView.as_view(), name="scan vin"),
    path(
        "scan-vin/success/",
        views.InstallScanVinNumberSuccessView.as_view(),
        name="scan vin success",
    ),
    path("assets/", views.InstallAssetListView.as_view(), name="asset list"),
    path("assets/create/", views.InstallAssetCreateView.as_view(), name="create asset"),
    path(
        "assets/<int:pk>/", views.InstallAssetDetailView.as_view(), name="detail asset"
    ),
    path(
        "assets/<int:pk>/update/",
        views.InstallAssetUpdateView.as_view(),
        name="update asset",
    ),
]
