import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from terminusgps_tracker.models.forms import (CustomerRegistrationForm,
                                              DriverForm, RegistrationForm,
                                              get_initial_imei_number)
from terminusgps_tracker.wialonapi.session import WialonSession

logger = logging.getLogger(__name__)

def form_customer_registration(request: HttpRequest) -> HttpResponse:
    context = {"title": "Registration"}
    if request.method == "POST" or request.htmx:
        context.update({"form": CustomerRegistrationForm(request.POST)})
    elif request.method == "GET":
        context.update({"form": CustomerRegistrationForm()})
    else:
        return HttpResponse(status=405)

    return render(request, "terminusgps_tracker/forms/customer_registration.html", context=context)

def form_registration(request: HttpRequest) -> HttpResponse:
    initial_data = get_initial_imei_number(request)

    if request.method == "POST":
        form = RegistrationForm(request.POST, initial=initial_data)
    else:
        form = RegistrationForm(initial=initial_data)

    if request.method == "POST" and form.is_valid():
        with WialonSession() as session:
            wialon_user_id = session.create_wialon_user(
                username=form.cleaned_data["email"],
                password=form.cleaned_data["wialon_password"],
            )
            session.assign_wialon_asset(
                user_id=wialon_user_id,
                asset_name=form.cleaned_data["asset_name"],
                imei_number=form.cleaned_data["imei_number"],
            )

        if "imei_number" in request.session:
            del request.session["imei_number"]

        request.session["to_addr"] = form.cleaned_data["email"]
        request.session["password"] = form.cleaned_data["wialon_password"]
        return redirect("form success")

    context = {"title": "Registration", "form": form}
    return render(request, "terminusgps_tracker/forms/registration.html", context)


def form_driver(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = DriverForm(request.POST)
    else:
        form = DriverForm()

    context = {"title": "Driver", "form": form}
    return render(request, "terminusgps_tracker/forms/driver.html", context)


def form_success_view(request: HttpRequest) -> HttpResponse:
    to_addr = request.session.get("to_addr", None)
    password = request.session.get("password", None)
    try:
        del request.session["to_addr"]
        del request.session["password"]
    except KeyError as e:
        raise KeyError(e)
    finally:
        return render(
            request, "terminusgps_tracker/forms/success.html", {"title": "Success!", "to_addr": to_addr, "password": password}
        )
