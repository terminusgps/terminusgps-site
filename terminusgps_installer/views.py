import typing
import urllib.parse

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from PIL import Image
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.django.utils import scan_barcode
from terminusgps.wialon import constants as wialon_constants
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSession, WialonSessionManager

from .forms import UnitCreationForm, VinNumberScanConfirmForm, VinNumberScanForm


class VinNumberScanFormView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Scan VIN #", "class": "flex flex-col gap-8"}
    form_class = VinNumberScanForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/partials/_scan_vin.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("installer:scan vin confirm")
    template_name = "terminusgps_installer/scan_vin.html"

    def form_valid(
        self, form: VinNumberScanForm
    ) -> HttpResponse | HttpResponseRedirect:
        """Scans the provided image for a VIN # barcode and redirects the client to a confirmation page if successful."""
        img = Image.open(form.cleaned_data["image"].file)
        results = scan_barcode(img)
        if not results:
            form.add_error(
                "image",
                ValidationError(
                    _(
                        "Whoops! No barcode was detected in the uploaded image. Please upload a new image."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)

        extracted_vin: str = results[0].data.decode("utf-8")
        return HttpResponseRedirect(self.get_success_url(extracted_vin))

    def get_success_url(self, vin_number: str | None = None) -> str:
        """Adds ``vin_number`` as a query parameter to :py:attr:`success_url` before returning it."""
        url = super().get_success_url()

        if vin_number:
            q = urllib.parse.urlencode({"vin_number": vin_number})
            url = f"{url}?{q}"
        return url


class VinNumberScanConfirmView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Confirm Scanned VIN #", "class": "flex flex-col gap-8"}
    form_class = VinNumberScanConfirmForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/partials/_scan_vin_confirm.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("installer:create unit")
    template_name = "terminusgps_installer/scan_vin_confirm.html"

    def get_initial(self, *args, **kwargs) -> dict[str, typing.Any]:
        """Adds ``vin_number`` to the form from query parameters."""
        initial: dict[str, typing.Any] = super().get_initial(*args, **kwargs)
        initial["vin_number"] = self.request.GET.get("vin_number", "")
        return initial

    def form_valid(
        self, form: VinNumberScanConfirmForm
    ) -> HttpResponse | HttpResponseRedirect:
        """Redirects the client to a unit creation form with the clean VIN #."""
        return HttpResponseRedirect(
            self.get_success_url(form.cleaned_data["vin_number"])
        )

    def get_success_url(self, vin_number: str | None = None) -> str:
        """Adds ``vin_number`` as a query parameter to :py:attr:`success_url` before returning it."""
        url = super().get_success_url()

        if vin_number:
            q = urllib.parse.urlencode({"vin_number": vin_number})
            url = f"{url}?{q}"
        return url


class VinNumberInfoView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "VIN # Info", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    template_name = "terminusgps_installer/vin_info.html"
    partial_template_name = "terminusgps_installer/partials/_vin_info.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`session_manager` to the view."""
        super().setup(request, *args, **kwargs)
        self.session_manager = WialonSessionManager(token=settings.WIALON_TOKEN)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds ``vin_info`` to the view context if ``vin_number`` was provided as a query parameter."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if self.request.GET.get("vin_number"):
            vin_number: str = self.request.GET.get("vin_number", "")
            session: WialonSession = self.session_manager.get_session(sid=None)
            info: dict[str, typing.Any] = wialon_utils.get_vin_info(vin_number, session)
            context["vin_info"] = info if info else None
        return context


class UnitCreationFormView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Unit Creation", "class": "flex flex-col gap-8"}
    form_class = UnitCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/partials/_create_unit.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("tracker:dashboard")
    template_name = "terminusgps_installer/create_unit.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.session_manager = WialonSessionManager(token=settings.WIALON_TOKEN)

    def get_form(self, form_class=None) -> UnitCreationForm:
        form = super().get_form(form_class=form_class)
        session = self.session_manager.get_session(sid=None)
        form.fields["hw_type"].choices = [
            (hw_type.get("id"), hw_type.get("name"))
            for hw_type in wialon_utils.get_hw_types(session)
        ]
        return form

    def get_initial(self, *args, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(*args, **kwargs)
        initial["vin_number"] = self.request.GET.get("vin_number", "")
        initial["imei_number"] = self.request.GET.get("imei_number", "")
        initial["account_id"] = self.request.GET.get(
            "account_id", settings.WIALON_ADMIN_ACCOUNT
        )
        return initial

    def form_valid(self, form: UnitCreationForm) -> HttpResponse | HttpResponseRedirect:
        vin_number: str = form.cleaned_data["vin_number"]
        imei_number: str = form.cleaned_data["imei_number"]
        account_id: str = form.cleaned_data["account_id"]
        hw_type_id: str = form.cleaned_data["hw_type"]
        session: WialonSession = self.session_manager.get_session(sid=None)
        resource: WialonResource = WialonResource(id=account_id, session=session)
        unit: WialonUnit | None = wialon_utils.get_unit_by_imei(imei_number, session)

        if resource is None or not resource.is_account:
            form.add_error(
                "account_id",
                ValidationError(
                    _("Whoops! Couldn't find Wialon account with id '%(account_id)s'."),
                    code="invalid",
                    params={"account_id": account_id},
                ),
            )
            return self.form_invalid(form=form)
        if unit is None:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Whoops! Couldn't find a Wialon unit with IMEI # '%(imei_number)s'."
                    ),
                    code="invalid",
                    params={"imei_number": imei_number},
                ),
            )
            return self.form_invalid(form=form)

        access_mask = wialon_constants.ACCESSMASK_UNIT_MIGRATION
        user = WialonUser(id=resource.creator_id, session=session)
        user.grant_access(unit, access_mask=access_mask)
        resource.migrate_unit(unit)
        unit.update_pfield(wialon_constants.WialonProfileField.VIN, vin_number)
        return super().form_valid(form=form)
