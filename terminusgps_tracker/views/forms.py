from typing import TypeVar

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
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
    field_template_name = "terminugps_tracker/forms/field.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs) -> HttpResponse | JsonResponse:
        form = self.form_class(request.POST)
        context = {"form": form}
        if "Hx-Request" in request.headers:
            html = {"html": render_to_string(self.field_template_name, context)}
            return JsonResponse(context | html)
        else:
            return render(request, self.template_name, context=context)


class PersonFormView(FormView):
    form_class = PersonForm
    initial = {}
    template_name = "terminugps_tracker/forms/person.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if "imei" in request.GET:
            request.session["imei_number"] = request.GET.get("imei", "")
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponse | JsonResponse:
        form = self.form_class(request.POST)
        context = {"form": form}
        if "Hx-Request" in request.headers:
            html = {"html": render_to_string(self.field_template_name, context)}
            return JsonResponse(context | html)
        else:
            return render(request, self.template_name, context=context)


class AssetFormView(FormView):
    form_class = AssetForm
    initial = {}
    template_name = "terminugps_tracker/forms/asset.html"


class ContactFormView(FormView):
    form_class = ContactForm
    initial = {}
    template_name = "terminugps_tracker/forms/contact.html"


def person_form(request: HttpRequest) -> HttpResponse:
    if not request.method == "POST":
        form = PersonForm()
    else:
        form = PersonForm(request.POST)
        if form.is_valid() and not request.headers.get("HX-Request", ""):
            request.session["first_name"] = form.cleaned_data["first_name"]
            request.session["last_name"] = form.cleaned_data["last_name"]
            return redirect("/register/", step="2")

    context = {
        "title": "Personal",
        "form": form,
        "step": 1,
    }
    return render(request, "terminusgps_tracker/forms/register.html", context=context)


def contact_form(request: HttpRequest) -> HttpResponse:
    if not request.method == "POST":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid() and not request.headers.get("HX-Request", ""):
            request.session["email"] = form.cleaned_data["email"]
            request.session["phone_number"] = form.cleaned_data["phone_number"]
            return redirect("/register/", step="3")

    context = {
        "title": "Contact",
        "form": form,
        "step": 2,
    }
    return render(request, "terminusgps_tracker/forms/register.html", context=context)


def asset_form(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid() and not request.headers.get("HX-Request", ""):
            request.session["asset_name"] = form.cleaned_data["asset_name"]
            request.session["imei_number"] = form.cleaned_data["imei_number"]
            return redirect("/register/", step="review")
        else:
            return render(
                request, "terminusgps_tracker/forms/field.html", context={"form": form}
            )
    else:
        form = AssetForm()
    context = {
        "title": "Asset",
        "form": form,
        "step": 3,
    }
    return render(request, "terminusgps_tracker/forms/register.html", context=context)


def registration_form(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid() and not request.headers.get("HX-Request", ""):
            raise NotImplementedError
    else:
        form = RegistrationForm(
            first_name=request.session["first_name"],
            last_name=request.session["last_name"],
            email=request.session["email"],
            phone_number=request.session["phone_number"],
            asset_name=request.session["asset_name"],
            imei_number=request.session["imei_number"],
        )
    context = {
        "title": "Review",
        "form": form,
        "step": "review",
    }
    return render(request, "terminusgps_tracker/forms/register.html", context=context)
