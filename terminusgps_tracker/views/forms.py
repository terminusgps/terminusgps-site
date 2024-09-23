from typing import Any

from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.conf import settings
from wialon import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.models.forms import GeofenceUploadForm, RegistrationForm
from terminusgps_tracker.wialonapi.items import WialonUnit, WialonResource, WialonUnitGroup, WialonUser
from terminusgps_tracker.wialonapi.session import WialonSession

DEFAULT_OWNER_ID = "27881459"

def form_success_view(request: HttpRequest) -> HttpResponse:
    context = {"redirect_url": "https://hosting.terminusgps.com"}
    return render(request, "terminusgps_tracker/forms/form_success.html", context=context)

class GeofenceUploadFormView(FormView):
    form_class = GeofenceUploadForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_geofence_upload.html"
    success_url = reverse_lazy("form success")
    initial = {}

    def form_valid(self, form: GeofenceUploadForm) -> HttpResponse:
        response = super().form_valid(form)
        return response

class RegistrationFormView(FormView):
    form_class = RegistrationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_registration.html"
    success_url = reverse_lazy("form success")
    initial = {}

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.imei_number: str = self.request.GET.get("imei", "")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["imei_number"] = self.imei_number
        context["title"] = "Registration Form"
        return context

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        response = super().form_valid(form)
        try:
            with WialonSession() as session:
                unit = self.get_wialon_unit(imei_number=form.cleaned_data["imei_number"], session=session)
                super_user = self.create_wialon_user(
                    username=f"Super {form.cleaned_data["first_name"]} {form.cleaned_data["last_name"]}",
                    password=form.cleaned_data["wialon_password_1"],
                    session=session,
                )
                end_user = self.create_wialon_user(
                    username=form.cleaned_data["email"],
                    password=form.cleaned_data["wialon_password_1"],
                    creator_id=str(super_user.id),
                    session=session
                )
                group = self.create_wialon_unit_group(
                    name=f"{form.cleaned_data["first_name"]} {form.cleaned_data["last_name"]}'s Group",
                    creator_id=str(super_user.id),
                    session=session,
                )
                group.add_unit(unit)
                super_user.assign_unit(unit, access_mask=flag.ACCESSFLAG_FULL_ACCESS)
                end_user.assign_unit(unit)
                end_user.assign_email(form.cleaned_data["email"])
                if form.cleaned_data["phone_number"]:
                    to_number: tuple[str, str] = "to_number", form.cleaned_data["phone_number"]
                    unit.add_afield(to_number)
                    end_user.assign_phone(form.cleaned_data["phone_number"])

        except WialonError as e:
            if settings.DEBUG:
                raise e
            else:
                form.add_error("imei_number", ValidationError(_("Something went wrong on our end. Please try again later."), code="invalid"))
                return self.form_invalid(form)

        return response

    def get_wialon_unit_id(self, imei_number: str, session: WialonSession) -> str | None:
        return session.get_id_from_iccid(imei_number)

    def get_wialon_unit(self, imei_number: str, session: WialonSession) -> WialonUnit:
        try:
            return WialonUnit(
                id=self.get_wialon_unit_id(imei_number, session=session),
                session=session,
            )
        except WialonError as e:
            raise e

    def create_wialon_user(
        self,
        username: str,
        password: str,
        *,
        creator_id: str = DEFAULT_OWNER_ID,
        session: WialonSession
    ) -> WialonUser:
        try:
            return WialonUser(
                creator_id=creator_id,
                name=username,
                password=password,
                session=session,
            )
        except WialonError as e:
            raise e

    def create_wialon_unit_group(
        self,
        name: str,
        *,
        creator_id: str = DEFAULT_OWNER_ID,
        session: WialonSession
    ) -> WialonUnitGroup:
        try:
            return WialonUnitGroup(
                creator_id=creator_id,
                name=name,
                session=session,
            )
        except WialonError as e:
            raise e

    def create_wialon_resource(
        self,
        name: str,
        *,
        creator_id: str = DEFAULT_OWNER_ID,
        session: WialonSession
    ) -> WialonResource:
        try:
            return WialonResource(
                creator_id=creator_id,
                name=name,
                session=session,
            )
        except WialonError as e:
            raise e
