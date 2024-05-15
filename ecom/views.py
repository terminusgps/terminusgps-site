from django.shortcuts import render, redirect
from django.http import JsonResponse

from ecom.forms import ProductForm

def handle404(request, exception):
    context = { "title": "404", "exception": exception }
    return render(request, "ecom/error/404.html", context=context, status=404)

def handle500(request, exception):
    context = { "title": "500", "exception": exception }
    return render(request, "ecom/error/500.html", context=context, status=500)

def home(request):
    context = { "title": "Shop" }
    return render(request, "ecom/shop.html", context=context)

def shop_all(request):
    context = { "title": "Shop All" }
    return render(request, "ecom/shopall.html", context=context)

def about(request):
    context = { "title": "About" }
    return render(request, "ecom/about.html", context=context)

def contact(request):
    context = { "title": "Contact" }
    return render(request, "ecom/contact.html", context=context)

def product(request, product_id):
    context = { "title": "Product" }
    return render(request, "ecom/product.html", context=context)

def cart(request):
    context = { "title": "Your Cart" }
    return render(request, "ecom/cart.html", context=context)

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("shop all")

    else:
        form = ProductForm()

    context = {
        "title": "Add Product",
        "form": form
    }

    return render(request, "ecom/addproduct.html", context=context)
