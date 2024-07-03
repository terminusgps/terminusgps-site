from django import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from terminusgps_tracker.decorators import requires_wialon_token
from terminusgps_tracker.models.wialon import WialonToken
from terminusgps_tracker.views.forms import (asset_form, contact_form,
                                             person_form, registration_form)
from terminusgps_tracker.wialonapi import WialonQuery, WialonSession


def dashboard(request: HttpRequest) -> HttpResponse:
    wialon_token, created = WialonToken.objects.get_or_create(user=request.user)
    if created:
        return auth(request, "wialon")
    context = {
        "title": "Dashboard",
    }
    return render(request, "terminusgps_tracker/dashboard.html", context=context)


def auth(request: HttpRequest, service: str) -> HttpResponse:
    match service:
        case "wialon":
            token = WialonToken.objects.get_or_create(user=request.user)[0]
            context = {
                "title": "Wialon Authentication",
                "auth_url": token.auth_url,
            }
        case "lightmetrics":
            raise NotImplementedError
        case _:
            return HttpResponse(status=400)
    return render(request, "terminusgps_tracker/auth.html", context=context)


def oauth2_callback(request: HttpRequest, service: str) -> HttpResponse:
    user = request.user
    match service:
        case "wialon":
            token = WialonToken.objects.get(user=user)
            token.access_token = request.GET.get("access_token")
            token.username = request.GET.get("user_name")
            token.save()

        case "lightmetrics":
            raise NotImplementedError

        case _:
            return HttpResponse(status=400)

    context = {
        "user": user,
        "token": token,
        "service": service,
    }

    return render(request, "terminusgps_tracker/oauth2_callback.html", context=context)


def registration(request: HttpRequest, step: str) -> HttpResponse:
    if step == "1":
        return person_form(request)
    elif step == "2":
        return contact_form(request)
    elif step == "3":
        return asset_form(request)
    elif step == "review":
        return registration_form(request)
    else:
        return HttpResponse(status=400)


@requires_wialon_token
def search_wialon(request: HttpRequest) -> HttpResponse:
    token = WialonToken.objects.get(user=request.user).access_token
    with WialonSession(token=token) as session:
        query = WialonQuery(prop_name="sys_user")
        items = query.execute(session).get("items", [])
        context = {
            "title": "Search Results",
            "items": items,
        }
    return render(request, "terminusgps_tracker/search_wialon.html", context=context)


@requires_wialon_token
def search(request: HttpRequest) -> HttpResponse:
    search = request.POST.get("search", "*")
    token = WialonToken.objects.get(user=request.user).access_token
    with WialonSession(token=token) as session:
        query = WialonQuery()
        query.prop_value_mask = search
        items = query.execute(session).get("items", [])
    context = {
        "items": items,
    }
    return render(request, "terminusgps_tracker/_wialon_results.html", context=context)


def validate_view(request: HttpRequest, form: forms.Form) -> HttpResponse:
    context = {"form": form}
    return render(request, "terminusgps_tracker/forms/field.html", context=context)
