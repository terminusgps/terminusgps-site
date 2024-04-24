from django.shortcuts import render

def home(request):
    context = { "title": "Blog" }
    return render(request, "blog/home.html", context=context)
