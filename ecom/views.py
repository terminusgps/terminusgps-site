from django.shortcuts import render

def handle404(request, exception):
    context = { "title": "404", "exception": exception }
    return render(request, "ecom/error/404.html", context=context, status=404)

def home(request):
    context = { "title": "Shop" }
    return render(request, "ecom/shop.html", context=context)

def shop_all(request):
    context = { "title": "Shop All" }
    return render(request, "ecom/shopall.html", context=context)

def about(request):
    context = { "title": "About" }
    return render(request, "ecom/faq.html", context=context)

def contact(request):
    context = { "title": "Contact" }
    return render(request, "ecom/contact.html", context=context)

def product(request, product_id):
    context = { "title": "Product" }
    return render(request, "ecom/product.html", context=context)

def faq(request):
    context = { "title": "FAQ" }
    return render(request, "ecom/faq.html", context=context)
