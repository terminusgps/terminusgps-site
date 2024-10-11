from django.urls import path

from . import views

urlpatterns = [
    path(
        "forms/register/",
        views.RegistrationFormView.as_view(),
        name="form registration",
    ),
    path("forms/login/", views.LoginFormView.as_view(), name="form login"),
    path("forms/logout/", views.LogoutFormView.as_view(), name="form logout"),
    path(
        "forms/asset_customization/",
        views.AssetCustomizationFormView.as_view(),
        name="form asset customization",
    ),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("forms/success/", views.form_success_redirect, name="form success"),
]
