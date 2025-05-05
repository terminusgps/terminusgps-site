from typing import Any

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from PIL import Image
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.django.utils import scan_barcode
from terminusgps.wialon.constants import WialonProfileField
from terminusgps.wialon.items import WialonResource
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_unit_by_imei

from .forms import VinNumberScanningForm, WialonAssetCreateForm, WialonAssetUpdateForm
from .models import Installer, WialonAccount, WialonAsset


class InstallDashboardView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    """
    A dashboard view for :model:`terminusgps_install.Installer` users.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Dashboard"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps_install/dashboard.html`

    **Partial Template:**
        :template:`terminusgps_install/partials/_dashboard.html`

    """

    content_type = "text/html"
    extra_context = {"title": "Dashboard", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_install/partials/_dashboard.html"
    template_name = "terminusgps_install/dashboard.html"
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login to view this content."
    raise_exception = False


class InstallScanVinNumberView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    """
    Scans an image for a barcode containing VIN number data.

    A :model:`terminusgps_install.Installer` takes a picture with their phone and uploads the image to the form.

    If a VIN number barcode is detected, it is extracted as a `utf-8`_ string from the barcode.

    If a VIN number is extracted properly, redirects the client to a success view including the extracted VIN number.

    **If any of the previous steps fail, rerenders the form with errors.**

    **Context**

    ``form``
        A Terminus GPS VIN number scanning form.

    ``title``
        The title for the view/webpage.

        Value: ``"Scan VIN #"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps_install/scan_vin.html`

    **Partial Template:**
        :template:`terminusgps_install/partials/_scan_vin.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    .. _utf-8: https://en.wikipedia.org/wiki/UTF-8

    """

    content_type = "text/html"
    extra_context = {"title": "Scan VIN #", "class": "flex flex-col gap-4"}
    form_class = VinNumberScanningForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_install/partials/_scan_vin.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("install:scan vin success")
    template_name = "terminusgps_install/scan_vin.html"

    def get_success_url(self, vin_number: str | None = None) -> str:
        """
        Returns a success url.

        :param vin_number: An optional vin number string. Default is :py:obj:`None`.
        :type vin_number: :py:obj:`str` | :py:obj:`None`
        :returns: An absolute success url.
        :rtype: :py:obj:`str`

        """
        if vin_number is not None:
            return f"{self.success_url}?vin={vin_number}"
        return self.success_url

    def form_valid(
        self, form: VinNumberScanningForm
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Scans an image for a VIN number barcode and extracts a VIN number from a found barcode.

        If the extraction is successful, redirects the client to a success view.

        :param form: A Terminus GPS Install VIN number scanning form.
        :type form: :py:obj:`~terminusgps_install.forms.VinNumberScanningForm`
        :raises ValidationError: If the VIN number scan fails.
        :returns: An HTTP redirect to a success view, if scan was successful.
        :rtype: :py:obj:`~django.http.HttpResponse` | :py:obj:`~django.http.HttpResponseRedirect`

        """
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


class InstallScanVinNumberSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    """
    :view:`terminusgps_install.InstallScanVinNumberView` redirects to this view if a VIN number was successfully extracted from an image.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"VIN # Scanned"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    ``vin_number``
        A VIN number retrieved from the query parameter ``vin``.

        Example: ``http://localhost:8000/<view>/?vin=<vin_number>``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps_install/scan_vin_success.html`

    **Partial Template:**
        :template:`terminusgps_install/partials/_scan_vin_success.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Vin # Scanned", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_install/partials/_scan_vin_success.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_install/scan_vin_success.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Adds ``vin_number`` to the view context based on the request query parameter ``vin``.

        :param kwargs: Keyword arguments for :py:meth:`get_context_data`.
        :returns: The view context.
        :rtype: :py:obj:`dict`

        """
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["vin_number"] = self.request.GET.get("vin", "")
        return context


class InstallAssetCreateView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    """
    Creates a :model:`terminusgps_install.WialonAsset` based on a VIN number and Wialon account.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Add Asset"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps_install/assets/create.html`

    **Partial Template:**
        :template:`terminusgps_install/assets/partials/_create.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Add Asset", "class": "flex flex-col gap-4"}
    form_class = WialonAssetCreateForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_create.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("install:dashboard")
    template_name = "terminusgps_install/assets/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.installer, _ = Installer.objects.get_or_create(user=request.user)

    def get_initial(self) -> dict[str, Any]:
        """
        Updates the form's initial ``vin_number`` field with a value from the HTTP request's query parameter ``vin``.

        If ``vin`` wasn't passed as a query parameter, ``vin_number`` is set to :py:obj:`None` instead.

        :returns: The initial form data.
        :rtype: :py:obj:`dict`

        """
        initial: dict[str, Any] = super().get_initial()
        initial["vin_number"] = self.request.GET.get("vin")
        return initial

    def get_form(self, form_class: forms.ModelForm | None = None) -> forms.ModelForm:
        """
        Updates the form with the installer's allowed accounts then returns the form.

        :param form_class: A model form class.
        :type form_class: :py:obj:`~django.forms.ModelForm` | :py:obj:`None`
        :returns: A model form object.
        :rtype: :py:obj:`~django.forms.ModelForm`

        """

        accounts = WialonAccount.objects.filter(installers=self.installer)
        form: forms.ModelForm = super().get_form(form_class=form_class)
        form.fields["account"].choices = accounts.order_by("name").values_list(
            "pk", "name"
        )
        return form

    def form_valid(self, form: forms.ModelForm) -> HttpResponse | HttpResponseRedirect:
        account_id: str = str(form.cleaned_data["account"].wialon_id)
        imei_number: str = form.cleaned_data["imei_number"]
        vin_number: str = form.cleaned_data["vin_number"]

        with WialonSession() as session:
            unit = get_unit_by_imei(imei_number, session=session)
            resource = WialonResource(account_id, session=session)

            if not unit:
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
            if not resource.is_account:
                form.add_error(
                    "account",
                    ValidationError(
                        _(
                            "Whoops! The selected Wialon resource with ID '%(account_id)s' isn't an account."
                        ),
                        code="invalid",
                        params={"account_id": account_id},
                    ),
                )

            # Add the VIN # to the unit and migrate it into the account
            unit.update_pfield(key=WialonProfileField.VIN, value=vin_number)
            resource.migrate_unit(unit)
            return super().form_valid(form=form)


class InstallAssetDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    """
    Renders a single :model:`terminusgps_install.WialonAsset`.

    **Context**

    ``title``
        The title for the view/webpage. Retrieved from the asset's name.

        Value: ``"Asset Details"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps_install/assets/detail.html`

    **Partial Template:**
        :template:`terminusgps_install/assets/partials/_detail.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Asset Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_install/assets/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Updates ``title`` in the view context to the :model:`terminusgps_install.WialonAsset` name.

        :param kwargs: Keyword arguments for :py:meth:`get_context_data`
        :returns: The view context.
        :rtype: :py:obj:`dict`

        """
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context


class InstallAssetUpdateView(LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView):
    """
    Updates a :model:`terminusgps_install.WialonAsset`.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Update Asset"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET
        - POST

    **Template:**
        :template:`terminusgps_install/assets/update.html`

    **Partial Template:**
        :template:`terminusgps_install/assets/partials/_update.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Update Asset", "class": "flex flex-col gap-4"}
    form_class = WialonAssetUpdateForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_update.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_install/assets/update.html"


class InstallAssetListView(LoginRequiredMixin, HtmxTemplateResponseMixin, ListView):
    """
    Renders a list of :model:`terminusgps_install.WialonAsset`.

    **Context**

    ``title``
        The title for the view/webpage.

        Value: ``"Asset List"``

    ``class``
        A `tailwindcss`_ class used for the view.

        Value: ``"flex flex-col gap-4"``

    **HTTP Methods:**
        - GET

    **Template:**
        :template:`terminusgps_install/assets/list.html`

    **Partial Template:**
        :template:`terminusgps_install/assets/partials/_list.html`

    .. _tailwindcss: https://tailwindcss.com/docs/installation/using-vite

    """

    content_type = "text/html"
    extra_context = {"title": "Asset List", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_install/assets/list.html"
