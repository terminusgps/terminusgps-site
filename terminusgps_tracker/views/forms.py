import logging
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from terminusgps_tracker.wialonapi import WialonSession
from terminusgps_tracker.models import RegistrationForm

logger = logging.getLogger(__name__)

def form_success_view(request: HttpRequest) -> HttpResponse:
    to_addr = request.session.get("to_addr", None)
    try:
        del request.session["to_addr"]
    except KeyError as e:
        raise KeyError(e)
    finally:
        return render(
            request, "terminusgps_tracker/forms/success.html", {"title": "Success!", "to_addr": to_addr}
        )

def form_registration(request: HttpRequest) -> HttpResponse:
    if not request.method == "POST":
        form = RegistrationForm()
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
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
            form.send_creds_email(form.cleaned_data["email"], form.cleaned_data["wialon_password"])
            request.session["to_addr"] = form.cleaned_data["email"]
            return redirect("form success")

    context = {"title": "Registration", "form": form}
    return render(request, "terminusgps_tracker/forms/registration.html", context)

def credentials_email_view(request: HttpRequest) -> HttpResponse:
    if not request.method == "GET":
        return HttpResponse(status=405)
    else:
        username, passw = request.GET.get("username", "Test Username"), request.POST.get("passw", "Test Password!1")
        context = {
            "username": username,
            "passw": passw,
            "login_link": "https://hosting.terminusgps.com/",
        }
        return render(request, "terminusgps_tracker/email_credentials.html", context)
