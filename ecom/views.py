from django.shortcuts import render

from .models import Product


def home(request):
    context = {"title": "Shop"}
    return render(request, "ecom/shop.html", context=context)


def shop_all(request):
    context = {"title": "Shop All"}
    return render(request, "ecom/shopall.html", context=context)


def about(request):
    context = {"title": "About"}
    return render(request, "ecom/about.html", context=context)


def contact(request):
    context = {"title": "Contact"}
    return render(request, "ecom/contact.html", context=context)


def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    context = {
        "title": f"Add {product.name}",
        "product": product,
    }
    return render(request, "ecom/add_to_cart.html", context=context)


def product(request, product_id):
    product = Product.objects.get(pk=product_id)
    context = {
        "title": product.name,
        "product": product,
    }
    return render(request, "ecom/product.html", context=context)


def cart(request):
    context = {"title": "Your Cart"}
    return render(request, "ecom/cart.html", context=context)
