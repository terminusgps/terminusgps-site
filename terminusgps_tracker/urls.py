from django.urls import path

from . import views

urlpatterns = [
    path(
        "forms/registration/",
        views.form_registration,
        name="form registration",
    ),
    path(
        "forms/driver/",
        views.form_driver,
        name="form driver",
    ),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("forms/success/", views.form_success_view, name="form success"),
    path("login/", views.form_login, name="form login"),
]
