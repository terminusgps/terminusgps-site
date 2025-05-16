from django.urls import path

from . import views

app_name = "installer"
urlpatterns = [
    path("scan/", views.VinNumberScanFormView.as_view(), name="scan vin"),
    path(
        "scan/success/",
        views.VinNumberScanSuccessView.as_view(),
        name="scan vin success",
    ),
    path("new/", views.UnitCreationFormView.as_view(), name="create unit"),
]
