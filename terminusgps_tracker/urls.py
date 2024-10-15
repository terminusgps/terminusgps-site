from django.urls import path

from . import views

urlpatterns = [
    path(
        "forms/register/",
        views.CustomerRegistrationView.as_view(),
        name="form registration",
    ),
    path(
        "forms/asset_customization/",
        views.CustomerAssetCustomizationView.as_view(),
        name="form asset customization",
    ),
    path(
        "forms/cc_upload/",
        views.CustomerCreditCardUploadView.as_view(),
        name="form cc upload",
    ),
]
