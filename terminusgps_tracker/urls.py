from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.CustomerRegistrationView.as_view(), name="register"),
    path("asset/", views.AssetCustomizationView.as_view(), name="asset"),
    path("upload/cc/", views.CreditCardUploadView.as_view(), name="upload credit card"),
    path("search_address/", views.search_address, name="search address"),
]
