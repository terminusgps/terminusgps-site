from django.urls import path

from . import views

urlpatterns = [
    path(
        "forms/registration/",
        views.form_registration,
        name="form registration",
    ),
    path("forms/success/", views.form_success_view, name="form success"),
]
