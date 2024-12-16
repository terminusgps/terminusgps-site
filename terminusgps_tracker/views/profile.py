from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.utils.translation import gettext_lazy as _
from wialon.api import WialonError

from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup
from terminusgps.wialon import flags

from terminusgps_tracker.forms import (
    AssetCreationForm,
    AssetModificationForm,
    SubscriptionModificationForm,
    NotificationCreationForm,
    NotificationDeletionForm,
    NotificationModificationForm,
    PaymentMethodCreationForm,
    PaymentMethodDeletionForm,
    PaymentMethodSetDefaultForm,
    ShippingAddressSetDefaultForm,
    ShippingAddressCreationForm,
    ShippingAddressDeletionForm,
)
from terminusgps_tracker.models import (
    TrackerPaymentMethod,
    TrackerShippingAddress,
    TrackerProfile,
    TrackerSubscriptionTier,
)


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/profile.html"
    extra_context = {
        "subtitle": settings.TRACKER_PROFILE["MOTD"],
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.user and request.user.is_authenticated:
            try:
                profile = TrackerProfile.objects.get(user=request.user)
            except TrackerProfile.DoesNotExist:
                profile = None
        else:
            profile = None
        self.profile = profile

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.profile:
            self.profile.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        if self.profile is not None:
            context["subscription"] = self.profile.subscription
        return context


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


class TrackerProfileSubscriptionView(LoginRequiredMixin, FormView):
    form_class = SubscriptionModificationForm
    template_name = "terminusgps_tracker/profile/subscription.html"
    extra_context = {"title": "Your Subscription"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def form_valid(self, form: SubscriptionModificationForm) -> HttpResponse:
        new_tier = TrackerSubscriptionTier.objects.get(pk=form.cleaned_data["tier"])
        print(self.subscription.__dir__())
        return super().form_valid(form=form)

    def post(self, request: HttpRequest, *args, **kwargs):
        print(request.POST)
        form = SubscriptionModificationForm(request.POST)
        print(form.is_valid())
        print(f"{form.errors = }")
        print(f"{[choice[0].__dir__() for choice in form.fields["tier"].choices] = }")
        return super().post(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.subscription = self.profile.subscription

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription"] = self.subscription
        return context

    def get_success_url(self) -> str:
        return reverse_lazy("modify subscription", kwargs={"id": self.subscription.pk})


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
    extra_context = {"title": "New Payment Method"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("payments")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        payment_profile = TrackerPaymentMethod.objects.create(profile=self.profile)
        payment_profile.save(form)
        return super().form_valid(form=form)


class TrackerProfilePaymentMethodDeletionView(LoginRequiredMixin, FormView):
    form_class = PaymentMethodDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_payment.html"
    extra_context = {"title": "Delete this payment method?"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("payments")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.payment_id = kwargs.get("id")

    def form_valid(self, form: PaymentMethodDeletionForm) -> HttpResponse:
        payment_id: int = form.cleaned_data["payment_id"]
        payment_profile = TrackerPaymentMethod.objects.get(
            profile=self.profile, authorizenet_id__exact=payment_id
        )
        payment_profile.delete()
        return super().form_valid(form=form)

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["payment_id"] = self.payment_id
        return initial

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        payment_id = self.payment_id

        context["payment_id"] = payment_id
        if payment_id is not None:
            context["payment_profile"] = (
                TrackerPaymentMethod.authorizenet_get_payment_profile(
                    self.profile.authorizenet_id, payment_id
                )
            )
        return context


class TrackerProfileShippingAddressDeletionView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressDeletionForm
    extra_context = {"title": "Delete Shipping Address?"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/forms/profile/delete_shipping_address.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.address_id = kwargs.get("id")

    def form_valid(self, form: PaymentMethodDeletionForm) -> HttpResponse:
        address_id: int = form.cleaned_data["address_id"]
        address = TrackerShippingAddress.objects.get(
            profile=self.profile, authorizenet_id__exact=address_id
        )
        address.delete()
        return super().form_valid(form=form)

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["address_id"] = self.address_id
        return initial

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        address_id = self.address_id

        context["address_id"] = address_id
        if address_id is not None:
            context["address"] = (
                TrackerShippingAddress.authorizenet_get_shipping_address(
                    self.profile.authorizenet_id, address_id
                )
            )
        return context


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
    extra_context = {"title": "Create Shipping Address"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address = TrackerShippingAddress.objects.create(profile=self.profile)
        address.save(form)
        return super().form_valid(form=form)
