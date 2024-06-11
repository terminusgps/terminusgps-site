from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.registration_form, name="register"),
    path("license/", views.license, name="license"),
]
