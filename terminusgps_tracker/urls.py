from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.registration_redirect, name="registration redirect"),
    path("registration/", views.registration_redirect, name="registration redirect"),
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
        "forms/registration/", views.registration_redirect, name="registration redirect"
    ),
    path(
        "forms/asset_customization/",
        views.AssetCustomizationView.as_view(),
        name="form asset customization",
    ),
]
