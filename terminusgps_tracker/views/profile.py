from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import QuerySet
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView, View
from wialon.api import WialonError

from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid

from terminusgps_tracker.forms import (
    PaymentMethodCreationForm,
    ShippingAddressCreationForm,
    AssetCreationForm,
)
from terminusgps_tracker.models import (
    TrackerPaymentMethod,
    TrackerProfile,
    TrackerShippingAddress,
    TrackerSubscription,
    TrackerAsset,
    TrackerAssetCommand,
)


class WialonUnitNotFoundError(Exception):
    """Raised when a Wialon unit was not found via IMEI #."""


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/profile.html"
    extra_context = {
        "title": "Your Profile",
        "subtitle": settings.TRACKER_PROFILE["MOTD"],
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            [asset.save(session) for asset in self.profile.assets.all()]
        return super().get(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.profile = (
                TrackerProfile.objects.get(user=request.user)
                if request.user and request.user.is_authenticated
                else None
            )
        except TrackerProfile.DoesNotExist:
            self.profile = (
                TrackerProfile.objects.create(user=request.user)
                if request.user and request.user.is_authenticated
                else None
            )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile is not None:
            context["title"] = f"{self.profile.user.first_name}'s Profile"
            context["assets"] = TrackerAsset.objects.filter(profile=self.profile)
            context["subscription"], _ = TrackerSubscription.objects.get_or_create(
                profile=self.profile
            )
        return context


class TrackerProfileSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/settings.html"
    extra_context = {
        "title": "Settings",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["addresses"] = self.get_addresses(self.profile)
        context["payments"] = self.get_payments(self.profile)
        return context

    @staticmethod
    def get_payments(profile: TrackerProfile, total: int = 4) -> list:
        if profile.payments.count() == 0:
            return []
        return [
            (
                TrackerPaymentMethod.authorizenet_get_payment_profile(
                    profile_id=profile.authorizenet_id,
                    payment_id=payment.authorizenet_id,
                ),
                payment.is_default,
            )
            for payment in profile.payments.all()[:total]
        ]

    @staticmethod
    def get_addresses(profile: TrackerProfile, total: int = 4) -> list:
        if profile.addresses.count() == 0:
            return []
        return [
            (
                TrackerShippingAddress.authorizenet_get_shipping_address(
                    profile_id=profile.authorizenet_id,
                    address_id=address.authorizenet_id,
                ),
                address.is_default,
            )
            for address in profile.addresses.all()[:total]
        ]


class TrackerProfileAssetCreationView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
    form_class = AssetCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_asset.html"
    partial_name = "terminusgps_tracker/forms/profile/partials/_create_asset.html"
    extra_context = {"title": "New Asset"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
    http_method_names = ["get", "post", "delete"]
    success_url = reverse_lazy("tracker profile")
    success_message = "%(name)s was added successfully."

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )

    def form_invalid(self, form: AssetCreationForm) -> HttpResponse:
        for field_name in form.errors.keys():
            form.fields[field_name].widget.attrs.update(
                {
                    "class": "w-full block mb-4 mt-2 p-2 rounded-md bg-red-50 text-terminus-red-700 placeholder-terminus-red-300",
                    "placeholder": "",
                }
            )
        return super().form_invalid(form=form)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        self.template_name = "terminusgps_tracker/blank.html"
        return self.render_to_response(context=self.get_context_data())

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        print(request.POST)
        return super().post(request, *args, **kwargs)

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        data: dict[str, str] = {"name": cleaned_data["asset_name"]}
        return self.success_message % data

    def get_available_commands(self) -> QuerySet:
        return TrackerAssetCommand.objects.filter().exclude(pk__in=[1, 2, 3])

    @transaction.atomic
    def wialon_create_asset(self, id: str, name: str, session: WialonSession) -> None:
        assert self.profile.wialon_end_user_id
        end_user_id = self.profile.wialon_end_user_id

        available = WialonUnitGroup(
            id=str(settings.WIALON_UNACTIVATED_GROUP), session=session
        )
        user = WialonUser(id=str(end_user_id), session=session)
        unit = WialonUnit(id=id, session=session)

        available.rm_item(unit)
        unit.rename(name)
        user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)

        asset = TrackerAsset.objects.create(id=unit.id, profile=self.profile)
        queryset = self.get_available_commands()
        asset.commands.set(queryset)
        asset.save()

    def form_valid(self, form: AssetCreationForm) -> HttpResponse:
        imei_number: str = form.cleaned_data["imei_number"]

        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                unit_id: str | None = get_id_from_iccid(imei_number, session=session)
                if not unit_id:
                    raise WialonUnitNotFoundError()

                self.wialon_create_asset(
                    unit_id, form.cleaned_data["asset_name"], session
                )
        except AssertionError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Couldn't find the Wialon user associated with this profile. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)
        except WialonUnitNotFoundError:
            form.add_error(
                None,
                ValidationError(
                    _("Unit with IMEI # '%(imei)s' may not exist, or wasn't found."),
                    code="invalid",
                    params={"imei": imei_number},
                ),
            )
            return self.form_invalid(form=form)
        except WialonError or ValueError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong with Wialon. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class TrackerProfilePaymentMethodCreationView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
    form_class = PaymentMethodCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_payment.html"
    partial_template = "terminusgps_tracker/forms/settings/create_payment.html"
    extra_context = {"title": "New Payment"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("profile settings")
    success_message = "Payment method was added successfully."

    def get(self, request: HttpRequest, *args, **kwargs):
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template
        return super().get(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        payment_profile = TrackerPaymentMethod.objects.create(profile=self.profile)
        payment_profile.save(form)
        return super().form_valid(form=form)


class TrackerProfilePaymentMethodDeletionView(LoginRequiredMixin, View):
    http_method_names = ["delete"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def delete(self, request: HttpRequest, id: str) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)

        last_4_digits = str(
            TrackerPaymentMethod.authorizenet_get_payment_profile(
                profile_id=self.profile.authorizenet_id, payment_id=int(id)
            )["payment"]["creditCard"]["cardNumber"]
        )[-4:]

        if request.headers.get("HX-Prompt") == last_4_digits:
            payment = self.profile.payments.get(authorizenet_id=int(id))
            payment.delete()
            return HttpResponse(status=200)
        return HttpResponse(status=406)


class TrackerProfileShippingAddressCreationView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
    form_class = ShippingAddressCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_shipping_address.html"
    partial_template = "terminusgps_tracker/forms/settings/create_address.html"
    extra_context = {"title": "Create Shipping Address"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")
    success_message = "Shipping address was added successfully."

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address = TrackerShippingAddress.objects.create(profile=self.profile)
        address.save(form)
        return super().form_valid(form=form)


class TrackerProfileShippingAddressDeletionView(LoginRequiredMixin, View):
    http_method_names = ["delete"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def delete(self, request: HttpRequest, id: str) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        address = self.profile.addresses.get(authorizenet_id=int(id))
        address.delete()
        return HttpResponse(status=200)
