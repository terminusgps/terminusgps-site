from django.shortcuts import render

def home(request):
    context = { "title": "Shop" }
    return render(request, "ecom/shop.html", context=context)

def shop_all(request):
    context = { "title": "Shop All" }
    return render(request, "ecom/shopall.html", context=context)
