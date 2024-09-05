from typing import Any

from django.urls import reverse_lazy
from django.views.generic import FormView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from wialon import flags as wialon_flag

from terminusgps_tracker.models.forms import RegistrationForm
from terminusgps_tracker.wialonapi.session import WialonSession

def form_success_view(request: HttpRequest) -> HttpResponse:
    context = {"redirect_url": "https://terminusgps.com/"}
    return render(request, "terminusgps_tracker/forms/form_success.html", context=context)

class RegistrationFormView(FormView):
    form_class = RegistrationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_registration.html"
    success_url = reverse_lazy("form success")
    initial = {}

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["imei_number"] = self.request.GET.get("imei", "")
        return initial

    def create_wialon_user(self, username: str, password: str) -> str:
        with WialonSession() as session:
            params = {
                "creatorId": "27881459",
                "name": username,
                "password": password,
                "dataFlags": wialon_flag.ITEM_DATAFLAG_BASE,
            }
            unit_id = session.wialon_api.core_create_user(**params).get("item").get("id")
        return unit_id

    def assign_unit_to_user(self, user_id: str, imei_number: str) -> None:
        with WialonSession() as session:
            unit_id = session.get_wialon_id(imei_number)
            params = {
                "userId": user_id,
                "itemId": unit_id,
                "accessMask": sum([
                    wialon_flag.ITEM_ACCESSFLAG_VIEW,
                    wialon_flag.ITEM_ACCESSFLAG_EDIT_NAME,
                    wialon_flag.ITEM_ACCESSFLAG_VIEW_PROPERTIES,
                    wialon_flag.ITEM_ACCESSFLAG_VIEW_CFIELDS,
                    wialon_flag.ITEM_ACCESSFLAG_EDIT_CFIELDS,
                    wialon_flag.ITEM_ACCESSFLAG_VIEW_ADMINFIELDS,
                    wialon_flag.ITEM_ACCESSFLAG_EXEC_REPORTS,
                ])
            }
            session.wialon_api.user_update_item_access(**params)
