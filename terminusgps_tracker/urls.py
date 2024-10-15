from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("forms/success/", views.form_success_redirect, name="form success"),
    path("forms/login/", views.CustomerLoginView.as_view(), name="form login"),
    path("forms/logout/", views.CustomerLogoutView.as_view(), name="form logout"),
    path(
        "forms/register/",
        views.CustomerRegistrationView.as_view(),
        name="form register",
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
