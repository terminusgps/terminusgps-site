from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from terminusgps_tracker.models.wialon import WialonToken


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


def oauth2_callback(request: HttpRequest) -> HttpResponse:
    access_token = request.GET.get("access_token")
    user_name = request.GET.get("user_name")
    if not access_token or user_name:
        return HttpResponse(status=400)

    wialon_token = WialonToken.objects.get_or_create(user=request.user)
    wialon_token.access_token = access_token
    wialon_token.save()

    context = {
        "user": request.user,
        "wialon_token": wialon_token,
    }

    return render(request, "terminusgps_tracker/oauth2_callback.html", context=context)
