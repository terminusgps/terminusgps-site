from django.urls import path

from . import views

urlpatterns = [
    path("", views.ecom_home, name="ecom_home"),
]
