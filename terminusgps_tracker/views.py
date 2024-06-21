from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def dashboard(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "Dashboard",
    }
    return render(request, "terminusgps_tracker/dashboard.html", context=context)


def auth(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "Authenticate",
    }
    return render(request, "terminusgps_tracker/auth.html", context=context)
