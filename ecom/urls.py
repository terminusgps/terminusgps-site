from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("all/", views.shop_all, name="shop_all"),
]
