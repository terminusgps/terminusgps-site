from typing import Any

from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from wialon import WialonError

from terminusgps_tracker.models.forms import RegistrationForm
from terminusgps_tracker.wialonapi.session import WialonSession

def form_success_view(request: HttpRequest) -> HttpResponse:
    context = {"redirect_url": "https://hosting.terminusgps.com/"}
    return render(request, "terminusgps_tracker/forms/form_success.html", context=context)

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
        return context

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        response = super().form_valid(form)
        full_name = " ".join((form.cleaned_data["first_name"], form.cleaned_data["last_name"]))
        username, password = form.cleaned_data["email"], form.cleaned_data["wialon_password_1"]
        with WialonSession() as session:
            try:
                # resource_id = session.create_resource(full_name + " Resource")
                group_id = session.create_group(full_name + " Unit Group")
                unit_id = session.get_id(form.cleaned_data["imei_number"])
                user_id = session.create_user(username, password)

                print(f"Renaming unit #{unit_id} to '{form.cleaned_data["asset_name"]}'...")
                self.rename_wialon_unit(unit_id, form.cleaned_data["asset_name"], session=session)
                print(f"Assigning user '{form.cleaned_data["email"]}' to unit '{form.cleaned_data["asset_name"]}'...")
                self.assign_user_to_unit(unit_id, user_id, session=session)
                print(f"Assigning unit '{form.cleaned_data["asset_name"]}' to group '#{group_id}'...")
                self.assign_units_to_group(list(unit_id), group_id, session=session)
                # print("Creating new account...")
                # self.create_wialon_account(resource_id, session=session)
                # print(f"Migrating user '{form.cleaned_data["email"]}' to new account...")
                # self.migrate_user_to_account(user_id, resource_id, session=session)
                if form.cleaned_data["phone_number"]:
                    print(f"Assigning '{form.cleaned_data["phone_number"]}' to '{form.cleaned_data["asset_name"]}'...")
                    self.assign_to_number_to_unit(unit_id, phone=form.cleaned_data["phone_number"], session=session)

            except WialonError:
                form.add_error("imei_number", ValidationError(_("Something went wrong on our end. Please try again later.")))
                return self.form_invalid(form)

        return response

    def migrate_user_to_account(self, user_id: str, resource_id: str, *, session: WialonSession) -> None:
        try:
            session.wialon_api.account_change_account(**{
                "itemId": user_id,
                "resourceId": resource_id,
            })
        except WialonError as e:
            raise e
        else:
            return

    def rename_wialon_unit(self, unit_id: str, name: str, *, session: WialonSession) -> None:
        try:
            session.wialon_api.item_update_name(**{
                "itemId": unit_id,
                "name": name,
            })
        except WialonError as e:
            raise e

    def create_wialon_account(self, resource_id: str, *, session: WialonSession) -> None:
        try:
            session.wialon_api.account_create_account(**{
                "itemId": resource_id,
                "plan": "Simple Terminus GPS",
            })
        except WialonError as e:
            raise e

    def assign_units_to_group(self, unit_ids: list[str], group_id: str, *, session: WialonSession) -> None:
        try:
            session.wialon_api.unit_group_update_units(**{
                "itemId": group_id,
                "units": unit_ids,
            })
        except WialonError as e:
            raise e

    def assign_to_number_to_unit(self, unit_id: str, phone: str, *, session: WialonSession) -> None:
        if not phone.startswith("+1"):
            phone = "".join(["+1", phone])
        try:
            session.wialon_api.update_custom_field(**{
                "itemId": unit_id,
                "callMode": "create",
                "n": "to_number",
                "v": phone,
            })
            session.wialon_api.unit_update_phone(**{
                "itemId": unit_id,
                "phoneNumber": phone,
            })
        except WialonError as e:
            raise e

    def assign_user_to_unit(self, unit_id: str, user_id: str, *, session: WialonSession) -> None:
        try:
            session.set_user_access_flags(unit_id, user_id)
        except WialonError as e:
            raise e
