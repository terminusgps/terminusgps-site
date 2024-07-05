from typing import Optional, TypeVar

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from terminusgps_tracker.models import PersonForm, RegistrationForm

GenericForm = TypeVar(
    "GenericForm",
    RegistrationForm,
    PersonForm,
)


class FormView(View):
    form_class = GenericForm
    initial = {}
    template_name = ""
    field_template = "terminusgps_tracker/forms/field.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.form_class(initial=self.initial)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.form_class(request.POST)
        if request.htmx:
            field_name = request.POST.get("hx_trigger_name")
            if field_name in form.changed_data:
                field = form[field_name]
                return render(
                    request, self.field_template, {"form": form, "field": field}
                )
        return render(request, self.template_name, {"form": form})


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    initial = {}
    template_name = "terminusgps_tracker/forms/registration.html"
