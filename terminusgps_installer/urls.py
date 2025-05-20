from django.urls import path

from . import views

app_name = "installer"
urlpatterns = [
    path("scan-vin/", views.VinNumberScanFormView.as_view(), name="scan vin"),
    path("scan-vin/info/", views.VinNumberInfoView.as_view(), name="scan vin info"),
    path(
        "scan-vin/confirm/",
        views.VinNumberScanConfirmView.as_view(),
        name="scan vin confirm",
    ),
    path("new/", views.UnitCreationFormView.as_view(), name="create unit"),
]
