import requests
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.template.response import HttpResponse

from .forms import get_form


def registration_flow(form) -> dict:
    url = "https://api.terminusgps.com/v2/forms/registration_form"
    json = {
        "email": form.cleaned_data["email"],
        "imei_number": form.cleaned_data["imei_number"],
        "asset_name": form.cleaned_data["asset_name"],
    }
    response = requests.post(url, json=json)
    return response.json()


def get_field(request: HttpRequest, field_name: str) -> HttpResponse:
    form = WialonRegistration(request.POST)
    context = {"field": form.fields[field_name]}
    return render(request, "dforms/partials/field.html", context=context)


def get_form(request: HttpRequest, form_name: str) -> HttpResponse:
    if not request.method == "POST":
        form = get_form(form_name)
    else:
        form = get_form(form_name, request.POST)
        if form.is_valid():
            registration_flow(form)

    context = {
        "title": form_name.title(),
        "client": settings.CLIENT,
        "form": form,
    }
    return render(request, "dforms/form.html", context=context)
