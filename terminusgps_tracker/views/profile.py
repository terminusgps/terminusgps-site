from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, FormView, TemplateView, View
from django.utils.translation import gettext_lazy as _
from wialon.api import WialonError

from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup
from terminusgps.wialon import flags

from terminusgps_tracker.forms import (
    AssetCreationForm,
    AssetModificationForm,
    NotificationCreationForm,
    NotificationDeletionForm,
    NotificationModificationForm,
    PaymentMethodCreationForm,
    PaymentMethodSetDefaultForm,
    ShippingAddressCreationForm,
    ShippingAddressSetDefaultForm,
)
from terminusgps_tracker.models import (
    TrackerPaymentMethod,
    TrackerProfile,
    TrackerShippingAddress,
    TrackerSubscription,
    TrackerSubscriptionTier,
)


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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if not request.user or not request.user.is_authenticated:
            self.profile = None
        else:
            self.profile, _ = TrackerProfile.objects.get_or_create(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription"] = TrackerSubscription.objects.get_or_create(
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
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["addresses"] = self.get_addresses(self.profile)
        context["payments"] = self.get_payments(self.profile)
        return context

    @classmethod
    def get_payments(cls, profile: TrackerProfile) -> list:
        if not profile.payments.filter().exists():
            return []
        return [
            (
                TrackerPaymentMethod.authorizenet_get_payment_profile(
                    profile_id=profile.authorizenet_id,
                    payment_id=payment.authorizenet_id,
                ),
                payment.is_default,
            )
            for payment in profile.payments.all()[:4]
        ]

    @classmethod
    def get_addresses(cls, profile: TrackerProfile) -> list:
        if not profile.addresses.filter().exists():
            return []
        return [
            (
                TrackerShippingAddress.authorizenet_get_shipping_address(
                    profile_id=profile.authorizenet_id,
                    address_id=address.authorizenet_id,
                ),
                address.is_default,
            )
            for address in profile.addresses.all()[:4]
        ]


class TrackerProfileAssetView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/assets.html"
    extra_context = {
        "title": "Your Units",
        "subtitle": "Register, modify, or delete your units",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    @classmethod
    def get_wialon_units(
        cls, profile: TrackerProfile, session: WialonSession
    ) -> list[dict[str, Any | None]]:
        unit_group = WialonUnitGroup(id=str(profile.wialon_group_id), session=session)
        units = [
            WialonUnit(id=unit_id, session=session) for unit_id in unit_group.items
        ]
        return [
            {
                unit.name: session.wialon_api.core_search_item(
                    **{
                        "id": unit.id,
                        "flags": sum(
                            [
                                flags.DATAFLAG_UNIT_BASE,
                                flags.DATAFLAG_UNIT_ADMIN_FIELDS,
                                flags.DATAFLAG_UNIT_CONNECTION_STATUS,
                                flags.DATAFLAG_UNIT_CUSTOM_FIELDS,
                                flags.DATAFLAG_UNIT_IMAGE,
                                flags.DATAFLAG_UNIT_POSITION,
                            ]
                        ),
                    }
                ).get("item")
            }
            for unit in units
        ]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.group_id = self.profile.wialon_group_id

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        with WialonSession() as session:
            context = self.get_context_data(session)
            return self.render_to_response(context=context)

    def get_context_data(
        self, wialon_session: WialonSession | None = None, **kwargs
    ) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if wialon_session:
            context["wialon_units"] = self.get_wialon_units(
                profile=self.profile, session=wialon_session
            )
            print(context["wialon_units"])
        return context


class TrackerProfileSubscriptionUpdateView(UpdateView):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = {"title": "Update Subscription"}
    template_name = "terminusgps_tracker/forms/profile/update_subscription.html"
    partial_name = (
        "terminusgps_tracker/forms/profile/partials/_update_subscription.html"
    )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().post(request, *args, **kwargs)


class TrackerProfileNotificationView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/notifications.html"
    extra_context = {
        "title": "Your Notifications",
        "subtitle": "Register, modify, or delete your notifications",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Notifications"
        return context


class TrackerProfilePaymentMethodView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/payments.html"
    extra_context = {"title": "Payment Methods"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        payment_ids: list[int] = self.get_payment_ids(profile=self.profile)
        context["payment_profiles"] = self.get_payment_profiles(
            profile_id=self.profile.authorizenet_id, payment_ids=payment_ids
        )
        return context

    @classmethod
    def get_shipping_address(cls, profile_id: int, address_id: int) -> dict[str, Any]:
        address = TrackerShippingAddress.authorizenet_get_shipping_address(
            profile_id, address_id
        ).get("address", {})

        return {
            "address_first_name": address.get("first_name"),
            "address_last_name": address.get("last_name"),
            "address_street": address.get("street"),
            "address_city": address.get("city"),
            "address_state": address.get("state"),
            "address_zip": address.get("zip"),
            "address_country": address.get("country"),
            "address_phone": address.get("phone"),
        }

    @classmethod
    def get_payment_ids(cls, profile: TrackerProfile) -> list[int]:
        if not profile.payments.all().exists():
            return []

        return [
            payment.authorizenet_id
            for payment in profile.payments.all()
            if payment.authorizenet_id is not None
        ]

    @classmethod
    def get_payment_profiles(cls, profile_id: int, payment_ids: list[int]) -> list:
        payment_profiles = [
            TrackerPaymentMethod.authorizenet_get_payment_profile(
                profile_id, payment_id
            )
            for payment_id in payment_ids
        ]
        return payment_profiles


class TrackerProfileAssetCreationView(LoginRequiredMixin, FormView):
    form_class = AssetCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_asset.html"
    extra_context = {"title": "New asset", "subtitle": "Register a new asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get("imei"):
            request.session["imei_number"] = request.GET.get("imei")
        return super().get(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if self.request.session.get("imei_number"):
            initial["imei_number"] = self.request.session["imei_number"]
        return initial

    def form_valid(self, form: AssetCreationForm) -> HttpResponse:
        try:
            imei_number: str = form.cleaned_data["imei_number"]
            asset_name: str = form.cleaned_data["asset_name"]
            self.create_asset(imei_number, asset_name, profile=self.profile)
        except WialonError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Whoops! Something went wrong with Wialon. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)
        except ValueError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Whoops! We tried to create the asset but couldn't find your profile. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)

    def create_asset(
        self, imei_number: str, asset_name: str, profile: TrackerProfile
    ) -> None:
        with WialonSession() as session:
            # Get unit id
            unit_id: str | None = get_id_from_iccid(imei_number, session=session)

            # Get Wialon objects
            user_group = WialonUnitGroup(
                id=str(profile.wialon_group_id), session=session
            )
            available_group = WialonUnitGroup(id="27890571", session=session)
            unit = WialonUnit(id=unit_id, session=session)

            # Perform actions
            available_group.rm_item(unit)
            user_group.add_item(unit)
            unit.rename(asset_name)


class TrackerProfileAssetModificationView(LoginRequiredMixin, FormView):
    form_class = AssetModificationForm
    template_name = "terminusgps_tracker/forms/profile/modify_asset.html"
    extra_context = {"title": "New asset", "subtitle": "Register a new asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(
        self, wialon_session: WialonSession | None = None, **kwargs
    ) -> dict[str, Any]:
        context: dict[str, Any] = self.get_context_data(**kwargs)
        if wialon_session:
            context["wialon_unit"] = wialon_session.wialon_api
        return context


class TrackerProfileNotificationCreationView(LoginRequiredMixin, FormView):
    form_class = NotificationCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_notification.html"
    extra_context = {"title": "New Notification"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)


class TrackerProfileNotificationDeletionView(LoginRequiredMixin, FormView):
    form_class = NotificationDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_notification.html"
    extra_context = {"title": "Delete Notification"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)


class TrackerProfileNotificationModificationView(LoginRequiredMixin, FormView):
    form_class = NotificationModificationForm
    template_name = "terminusgps_tracker/forms/profile/modify_notification.html"
    extra_context = {"title": "Modify Notification"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)


class TrackerProfilePaymentMethodCreationView(LoginRequiredMixin, FormView):
    form_class = PaymentMethodCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_payment.html"
    partial_template = "terminusgps_tracker/forms/settings/create_payment.html"
    extra_context = {"title": "New Payment"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("profile settings")

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
    raise_exception = False

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


class TrackerProfileShippingAddressDeletionView(LoginRequiredMixin, View):
    http_method_names = ["delete"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def delete(self, request: HttpRequest, id: str) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        address = self.profile.addresses.get(authorizenet_id=int(id))
        address.delete()
        return HttpResponse(status=200)


class TrackerProfileShippingAddressView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/shipping.html"
    extra_context = {"title": "Shipping Addresses"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        address_ids: list[int] = self.get_address_ids(profile=self.profile)
        context["addresses"] = self.get_addresses(
            profile_id=self.profile.authorizenet_id, address_ids=address_ids
        )
        return context

    @classmethod
    def get_shipping_address(cls, profile_id: int, address_id: int) -> dict[str, Any]:
        address = TrackerShippingAddress.authorizenet_get_shipping_address(
            profile_id, address_id
        )
        return address

    @classmethod
    def get_address_ids(cls, profile: TrackerProfile) -> list[int]:
        if not profile.addresses.all().exists():
            return []

        return [
            address.authorizenet_id
            for address in profile.addresses.all()
            if address.authorizenet_id is not None
        ]

    @classmethod
    def get_addresses(cls, profile_id: int, address_ids: list[int]) -> list:
        addresses = [
            TrackerShippingAddress.authorizenet_get_shipping_address(
                profile_id, address_id
            )
            for address_id in address_ids
        ]
        return addresses


class TrackerProfileShippingAddressSetDefaultView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressSetDefaultForm
    template_name = "terminusgps_tracker/forms/profile/default_shipping_address.html"
    extra_context = {
        "title": "Update Shipping Address",
        "subtitle": "Set this shipping address to default?",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.address_id = kwargs["id"]

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["address_id"] = self.address_id
        return initial

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["address_id"] = self.address_id
        context["address"] = TrackerShippingAddress.authorizenet_get_shipping_address(
            profile_id=self.profile.authorizenet_id, address_id=self.address_id
        )
        return context

    def form_valid(self, form: PaymentMethodSetDefaultForm) -> HttpResponse:
        address = self.profile.addresses.filter().get(
            authorizenet_id__exact=form.cleaned_data["payment_id"]
        )
        address.is_default = True
        address.save()
        return super().form_valid(form=form)


class TrackerProfilePaymentMethodSetDefaultView(LoginRequiredMixin, FormView):
    form_class = PaymentMethodSetDefaultForm
    template_name = "terminusgps_tracker/forms/profile/default_payment.html"
    extra_context = {
        "title": "Update Payment Method",
        "subtitle": "Set this payment method to default?",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.payment_id = kwargs["id"]

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["payment_id"] = self.payment_id
        return initial

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["payment_id"] = self.payment_id
        context["payment_profile"] = (
            TrackerPaymentMethod.authorizenet_get_payment_profile(
                profile_id=self.profile.authorizenet_id, payment_id=self.payment_id
            )
        )
        return context

    def form_valid(self, form: PaymentMethodSetDefaultForm) -> HttpResponse:
        payment = self.profile.payments.filter().get(
            authorizenet_id__exact=form.cleaned_data["payment_id"]
        )
        payment.is_default = True
        payment.save()
        return super().form_valid(form=form)


class TrackerProfileShippingAddressCreationView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_shipping_address.html"
    partial_template = "terminusgps_tracker/forms/settings/create_address.html"
    extra_context = {"title": "Create Shipping Address"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

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
