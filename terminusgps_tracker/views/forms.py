from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import FormView

from terminusgps_tracker.models import RegistrationForm


def form_success_view(request: HttpRequest) -> HttpResponse:
    return render(
        request, "terminusgps_tracker/forms/success.html", {"title": "Success!"}
    )


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = "terminusgps_tracker/forms/registration_form.html"
    field_template_name = "terminusgps_tracker/forms/field.html"
    field_order = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "asset_name",
        "imei_number",
    ]
    success_url = "/forms/success/"
