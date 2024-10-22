from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.CustomerRegistrationView.as_view(), name="register"),
    path("asset/", views.AssetCustomizationView.as_view(), name="asset"),
]
