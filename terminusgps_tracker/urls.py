from django.urls import path

from . import views

urlpatterns = [
    path(
        "forms/registration/",
        views.RegistrationFormView.as_view(),
        name="registration form",
    ),
]
