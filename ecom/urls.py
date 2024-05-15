from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("all/", views.shop_all, name="shop all"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    path("addproduct/", views.add_product, name="add product"),

    path("cart/", views.cart, name="cart"),

    path("<int:id>/", views.product, name="product"),
]
