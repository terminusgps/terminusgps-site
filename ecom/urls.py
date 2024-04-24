from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("all/", views.shop_all, name="shop all"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("p/<int:id>/", views.product, name="product"),
]
