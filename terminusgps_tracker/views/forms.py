import logging
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from terminusgps_tracker.wialonapi import WialonSession
from terminusgps_tracker.models import RegistrationForm

logger = logging.getLogger(__name__)

def form_success_view(request: HttpRequest) -> HttpResponse:
    return render(
        request, "terminusgps_tracker/forms/success.html", {"title": "Success!"}
    )

def form_registration(request: HttpRequest) -> HttpResponse:
    if not request.method == "POST":
        form = RegistrationForm()
    else:
        print(request.POST)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with WialonSession() as session:
                wialon_password = session.generate_wialon_password(12)
                wialon_user_id = session.create_wialon_user(
                    username=form.cleaned_data["email"],
                    password=wialon_password,
                )
                session.assign_wialon_asset(
                    user_id=wialon_user_id,
                    asset_name=form.cleaned_data["asset_name"],
                    imei_number=form.cleaned_data["imei_number"],
                )
            form.send_creds_email(form.cleaned_data["email"], wialon_password)
            return redirect("form success")

    context = {"title": "Registration", "form": form}
    return render(request, "terminusgps_tracker/forms/registration.html", context)
