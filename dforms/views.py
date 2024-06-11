import requests
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.template.response import HttpResponse

from .forms import WialonRegistration


def registration_flow(form) -> dict:
    url = "https://api.terminusgps.com/v2/forms/registration_form"
    json = {
        "email": form.cleaned_data["email"],
        "imei_number": form.cleaned_data["imei_number"],
        "asset_name": form.cleaned_data["asset_name"],
    }
    response = requests.post(url, json=json)
    return response.json()


def registration_form(request: HttpRequest) -> HttpResponse:
    if not request.method == "POST":
        form = WialonRegistration()
    else:
        form = WialonRegistration(request.POST)
        if form.is_valid():
            registration_flow(form)

    context = {
        "title": "Register",
        "client": settings.CLIENT,
        "form": form,
    }
    return render(request, "dforms/form.html", context=context)


def license(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "License",
        "client": settings.CLIENT,
        "license": {
            "name": "GNU GENERAL PUBLIC LICENSE Version 3",
            "url": "https://www.gnu.org/licenses/gpl-3.0.html",
        },
    }
    return render(request, "dforms/license.html", context=context)
