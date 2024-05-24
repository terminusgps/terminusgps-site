from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("all/", views.shop_all, name="shop all"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("<int:product_id>/", views.product, name="product"),
    path("cart/<int:product_id>/", views.add_to_cart, name="add to cart"),
]
