from typing import Any

from authorizenet.apicontractsv1 import paymentProfile
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.utils.translation import gettext_lazy as _
from wialon.api import WialonError

from terminusgps_tracker.forms.payments import ShippingAddressModificationForm
from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.integrations.wialon.items import WialonUnit, WialonUnitGroup
from terminusgps_tracker.integrations.wialon.items.base import WialonBase
from terminusgps_tracker.integrations.wialon.items.user import WialonUser
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.utils import get_id_from_iccid
from terminusgps_tracker.models.profile import TrackerProfile
from terminusgps_tracker.models.todo import TrackerTodoList
from terminusgps_tracker.forms import (
    AssetCreationForm,
    AssetDeletionForm,
    AssetModificationForm,
    SubscriptionCreationForm,
    SubscriptionDeletionForm,
    SubscriptionModificationForm,
    NotificationCreationForm,
    NotificationDeletionForm,
    NotificationModificationForm,
    PaymentMethodCreationForm,
    PaymentMethodDeletionForm,
    ShippingAddressCreationForm,
    ShippingAddressDeletionForm,
)
from terminusgps_tracker.models import (
    TrackerSubscription,
    TrackerPaymentMethod,
    TrackerShippingAddress,
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
        self.profile = None
        if request.user.is_authenticated:
            self.profile = TrackerProfile.objects.get(user=self.request.user)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.profile:
            self.profile.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile is not None:
            title = f"{self.profile.user.first_name}'s Profile"
            todo_list, _ = TrackerTodoList.objects.get_or_create(profile=self.profile)
            subscription, _ = TrackerSubscription.objects.get_or_create(
                profile=self.profile
            )

            context["title"] = title
            context["todos"] = todo_list.todo_items.all()
            context["subscription_tier"] = subscription.curr_tier
        return context


class TrackerProfileAssetView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/assets.html"
    extra_context = {
        "title": "Your Assets",
        "subtitle": "Register, modify, or delete your assets",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

        if not request.session.get("wialon_session_id"):
            session = WialonSession()
            session.login(session.token)
            request.session["wialon_session_id"] = session.id

    def get_wialon_items(self, session: WialonSession) -> list[str]:
        group_id: str = str(self.profile.wialon_group_id)
        group = WialonUnitGroup(id=group_id, session=session)
        return group.items

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        with WialonSession() as session:
            wialon_items = self.get_wialon_items(session=session)
            wialon_user = WialonUser(
                id=str(self.profile.wialon_user_id), session=session
            )
            wialon_units = [
                WialonUnit(id=str(unit_id), session=session) for unit_id in wialon_items
            ]

            context["wialon_user"] = wialon_user
            context["wialon_items"] = wialon_items
            context["wialon_units"] = wialon_units
        print(context)
        return context


class TrackerProfileSubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/subscription.html"
    extra_context = {}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription"] = self.profile.subscription
        return context


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
    extra_context = {
        "title": "Your payment methods",
        "subtitle": "Register, modify, or delete your payment methods",
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
        payment_ids: list = self.get_payment_ids()
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Payment Methods"
        if self.profile.address:
            context["shipping_address"] = self.get_shipping_address()
        if payment_ids:
            context["payment_profiles"] = self.get_payment_profiles(payment_ids)
        return context

    def get_payment_ids(self) -> list[int]:
        if not self.profile.payments.all().exists():
            return []

        return [
            payment.authorizenet_id
            for payment in self.profile.payments.all()
            if payment.authorizenet_id is not None
        ]

    def get_payment_profiles(self, payment_ids: list[int]) -> list:
        return [
            TrackerPaymentMethod.get_authorizenet_payment_profile(
                int(self.profile.customerProfileId), payment_id
            )
            for payment_id in payment_ids
        ]

    def get_shipping_address(self) -> dict[str, Any]:
        if not self.profile.customerProfileId:
            return {}

        profile_id: int = int(self.profile.customerProfileId)
        address_id: int | None = self.profile.address.authorizenet_id or None
        address = TrackerShippingAddress.get_authorizenet_address(
            profile_id, address_id
        ).get("address", {})

        return {
            "address_street": address.get("street"),
            "address_city": address.get("city"),
            "address_state": address.get("state"),
            "address_zip": address.get("zip"),
            "address_country": address.get("country"),
            "address_phone": address.get("phone"),
        }


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
        if request.user.is_authenticated:
            self.profile = TrackerProfile.objects.get(user=request.user)
        else:
            self.profile = None

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
        if self.profile is None:
            return HttpResponseRedirect(self.login_url, status=401)

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


class TrackerProfileAssetDeletionView(LoginRequiredMixin, FormView):
    form_class = AssetDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_asset.html"
    extra_context = {
        "title": "Delete asset",
        "subtitle": "Delete an asset from your account",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: AssetDeletionForm) -> HttpResponse:
        imei_number: str = form.cleaned_data["imei_number"]

        try:
            self.delete_asset(imei_number, profile=self.profile)
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
        return super().form_valid(form=form)

    def delete_asset(
        self, imei_number: str, profile: TrackerProfile | None = None
    ) -> None:
        if profile is None:
            raise ValueError("Cannot delete asset without a profile to delete it from")

        with WialonSession() as session:
            # Get unit id
            unit_id = get_id_from_iccid(imei_number, session=session)

            # Get Wialon objects
            unit = WialonUnit(id=unit_id, session=session)
            user_group = WialonUnitGroup(
                id=str(profile.wialon_group_id), session=session
            )

            # Perform actions
            if str(unit.id) in user_group.items:
                user_group.rm_item(unit)
                unit.rename(str(unit.uid))


# TODO: Add more fields for an asset
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


class TrackerProfileSubscriptionCreationView(LoginRequiredMixin, FormView):
    form_class = SubscriptionCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_subscription.html"
    extra_context = {
        "title": "Create subscription",
        "subtitle": "Select a subscription tier to get started!",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: SubscriptionCreationForm) -> HttpResponse:
        todo_item = self.profile.todo_list.todo_items.filter(view=str(self)).first()
        if todo_item.exists() and not todo_item.is_complete:
            todo_item.is_complete = True
            todo_item.save()
        return super().form_valid(form=form)


class TrackerProfileSubscriptionDeletionView(LoginRequiredMixin, FormView):
    form_class = SubscriptionDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_subscription.html"
    extra_context = {
        "title": "Cancel subscription",
        "subtitle": "Are you sure you want to cancel your subscription?",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile and self.profile.subscription:
            context["subtitle"] = (
                f"Are you sure you want to cancel your {self.profile.subscription.tier_display_gradient} subscription?"
            )
        return context

    def form_valid(self, form: SubscriptionDeletionForm) -> HttpResponse:
        self.delete_subscription(profile=self.profile)
        return super().form_valid(form=form)

    def delete_subscription(self, profile: TrackerProfile) -> None:
        if profile.subscription is not None:
            profile.subscription = None
            profile.save()


class TrackerProfileSubscriptionModificationView(LoginRequiredMixin, FormView):
    form_class = SubscriptionModificationForm
    template_name = "terminusgps_tracker/forms/profile/modify_subscription.html"
    extra_context = {
        "title": "Modify Subscription",
        "subtitle": "Modify your subscription",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)


class TrackerProfileNotificationCreationView(LoginRequiredMixin, FormView):
    form_class = NotificationCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_notification.html"
    extra_context = {
        "title": "New Notification",
        "subtitle": "Create a new notification",
    }
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
    extra_context = {
        "title": "Delete Notification",
        "subtitle": "Delete a notification",
    }
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
    extra_context = {
        "title": "Modify Notification",
        "subtitle": "Modify a notification",
    }
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
    extra_context = {
        "title": "New Payment Method",
        "subtitle": "Add a new payment method",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("payments")
    success_message = "%(username)s's payment method was properly added"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        payment = TrackerPaymentMethod.objects.create(profile=self.profile)
        payment.save(form=form)
        return super().form_valid(form=form)

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username")
        )


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

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["payment_id"] = self.payment_id
        return initial

    def form_valid(self, form: PaymentMethodDeletionForm) -> HttpResponse:
        try:
            self.delete_payment_profile(form=form)
        except TrackerPaymentMethod.DoesNotExist:
            form.add_error(
                None,
                _("Whoops! Something went wrong on our end. Please try again later."),
            )
            return self.form_invalid(form=form)
        except ValueError:
            form.add_error(
                None,
                _("Whoops! Something went wrong on our end. Please try again later."),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["payment_id"] = self.payment_id
        context["payment_profile"] = self.get_payment_profile(self.payment_id)
        return context

    @transaction.atomic
    def delete_payment_profile(self, form: PaymentMethodDeletionForm) -> None:
        payment_id: int = form.cleaned_data["payment_id"]
        payment_obj: TrackerPaymentMethod = TrackerPaymentMethod.objects.get(
            profile=self.profile, authorizenet_id__exact=payment_id
        )
        payment_obj.delete_authorizenet_payment_profile(
            int(self.profile.customerProfileId), payment_id
        )
        payment_obj.delete()

    def get_payment_profile(self, payment_id: int | None) -> dict[str, Any] | None:
        if payment_id is None:
            return
        return TrackerPaymentMethod.get_authorizenet_payment_profile(
            int(self.profile.customerProfileId), payment_id
        )


class TrackerProfileShippingAddressView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressModificationForm
    template_name = "terminusgps_tracker/profile/shipping.html"
    extra_context = {"title": "Your Shipping Address"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_initial(self) -> dict[str, Any]:
        return self.get_addr_from_authorizenet()

    def get_addr_from_authorizenet(self) -> dict[str, Any]:
        if not self.profile.customerProfileId:
            return {}

        customer_id: int = int(self.profile.customerProfileId)
        address_id: int | None = self.profile.address.authorizenet_id or None
        address = TrackerShippingAddress.get_authorizenet_address(
            customer_id, address_id
        ).get("address", {})

        return {
            "address_street": address.get("street"),
            "address_city": address.get("city"),
            "address_state": address.get("state"),
            "address_zip": address.get("zip"),
            "address_country": address.get("country"),
            "address_phone": address.get("phone"),
        }


class TrackerProfileShippingAddressCreationView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
    form_class = ShippingAddressCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_shipping_address.html"
    extra_context = {
        "title": "Create Shipping Address",
        "subtitle": "Enter your address below.",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")
    success_message = "%(username)s's shipping address was properly set"

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address_obj, _ = TrackerShippingAddress.objects.get_or_create(
            profile=self.profile
        )
        address_obj.save(form=form)
        return super().form_valid(form=form)

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username")
        )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)


class TrackerProfileShippingAddressDeletionView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_shipping_address.html"
    extra_context = {
        "title": "Delete Shipping Address",
        "subtitle": "Are you sure you want to clear your shipping address?",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
