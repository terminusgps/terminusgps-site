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
    path(
        "forms/customer_registration/",
        views.form_customer_registration,
        name="form customer registration",
    ),
    path(
        "forms/customer_login/",
        views.form_customer_login,
        name="form customer login",
    ),
    path("forms/success/", views.form_success_view, name="form success"),
    path("docs/<str:page_name>/", views.documentation_view, name="doc view")
]
