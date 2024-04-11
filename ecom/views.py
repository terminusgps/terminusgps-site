from django.shortcuts import render

def ecom_home(request):
    context = { "title": "Home" }
    return render(request, "ecom/home.html", context=context)
