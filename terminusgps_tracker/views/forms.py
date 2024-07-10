from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
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
    success_url = reverse_lazy("/forms/success/")

    def email_credentials(self, to_addr: str) -> None:
        """Email the Wialon username and password to the provided email address."""
        raise NotImplementedError

    def form_valid(self, form: RegistrationForm):
        form = form.save()
        self.email_credentials(to_addr=form.cleaned_data["email"])
        messages.success(
            self.request,
            f"Registration complete! Your asset has been registered and your new Wialon credentials have been emailed to {form.cleaned_data['email']}.",
        )

        return super().form_valid(form)
