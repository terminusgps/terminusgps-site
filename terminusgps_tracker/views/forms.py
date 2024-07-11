import logging
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

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
            form.send_cred_email(form.cleaned_data["email"])
            form.save()
            return redirect("form success")

    context = {"title": "Registration", "form": form}
    return render(request, "terminusgps_tracker/forms/registration.html", context)
