from typing import TypeVar

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View

from terminusgps_tracker.models import (AssetForm, ContactForm, PersonForm,
                                        RegistrationForm)

GenericForm = TypeVar(
    "GenericForm",
    AssetForm,
    ContactForm,
    PersonForm,
    RegistrationForm,
)


class FormView(View):
    form_class = GenericForm
    initial = {}
    template_name = ""
    base_field_template = "terminusgps_tracker/forms/fields/base.html"
    ok_field_template = "terminusgps_tracker/forms/fields/ok.html"
    err_field_template = "terminusgps_tracker/forms/fields/err.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            request.session["imei_number"]
        except KeyError:
            request.session["imei_number"] = request.GET.get("imei", "")

        if self.form_class is ContactForm and not self.initial:
            self.initial.update({"imei_number": request.session["imei_number"]})

        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = self.form_class(request.POST)
        context = {"form": form}
        if "Hx-Request" in request.headers:
            field = form.changed_data[0]
            context.update({"field": field})
            if not form.errors:
                template = self.ok_field_template
            else:
                template = self.err_field_template
            return render(request, template, context=context)
        else:
            return render(request, self.template_name, context=context)


class PersonFormView(FormView):
    form_class = PersonForm
    initial = {}
    template_name = "terminusgps_tracker/forms/person.html"


class AssetFormView(FormView):
    form_class = AssetForm
    initial = {}
    template_name = "terminusgps_tracker/forms/asset.html"


class ContactFormView(FormView):
    form_class = ContactForm
    initial = {}
    template_name = "terminusgps_tracker/forms/contact.html"


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    initial = {}
    template_name = "terminusgps_tracker/forms/register.html"
