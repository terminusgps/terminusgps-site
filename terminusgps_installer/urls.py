from django.urls import path

from . import views

app_name = "installer"
urlpatterns = [
    path("", views.InstallerDashboardView.as_view(), name="dashboard"),
    path("jobs/", views.InstallJobListView.as_view(), name="job list"),
    path("jobs/create/", views.InstallJobCreateView.as_view(), name="job create"),
    path("jobs/<int:pk>/", views.InstallJobDetailView.as_view(), name="job detail"),
    path(
        "jobs/<int:pk>/complete/",
        views.InstallJobCompleteView.as_view(),
        name="job complete",
    ),
    path(
        "jobs/<int:pk>/complete/success/",
        views.InstallJobCompleteSuccessView.as_view(),
        name="job complete success",
    ),
    path(
        "commands/<int:asset_pk>/",
        views.WialonAssetCommandListView.as_view(),
        name="command list",
    ),
    path(
        "commands/<int:asset_pk>/<int:pk>/",
        views.WialonAssetCommandDetailView.as_view(),
        name="command detail",
    ),
    path(
        "commands/<int:asset_pk>/<int:pk>/execute/",
        views.WialonAssetCommandExecuteView.as_view(),
        name="command execute",
    ),
    path(
        "commands/<int:asset_pk>/<int:pk>/execute/success/",
        views.WialonAssetCommandExecuteSuccessView.as_view(),
        name="command execute success",
    ),
    path(
        "assets/<int:pk>/", views.WialonAssetDetailView.as_view(), name="asset detail"
    ),
    path(
        "assets/<int:pk>/update/",
        views.WialonAssetUpdateView.as_view(),
        name="asset update",
    ),
    path(
        "assets/<int:pk>/position/",
        views.WialonAssetPositionView.as_view(),
        name="asset position",
    ),
]
