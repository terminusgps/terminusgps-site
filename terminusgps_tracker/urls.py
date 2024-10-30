from django.urls import path

from . import views

urlpatterns = [
    path("forms/success/", views.FormSuccessView.as_view(), name="form success"),
    path("upload/asset/", views.AssetUploadView.as_view(), name="upload asset"),
    path(
        "upload/payment/", views.CreditCardUploadView.as_view(), name="upload payment"
    ),
    path("search_address/", views.SearchAddress.as_view(), name="search address"),
    path(
        "upload/payment/help/", views.CreditCardHelpView.as_view(), name="help payment"
    ),
    path("upload/asset/help/", views.AssetHelpView.as_view(), name="help asset"),
]
