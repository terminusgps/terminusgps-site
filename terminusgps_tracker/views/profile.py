from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.utils.translation import gettext_lazy as _
from authorizenet.apicontractsv1 import (
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    paymentType,
)
from authorizenet.apicontrollers import createCustomerPaymentProfileController
from wialon.api import WialonError

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.integrations.wialon.items import WialonUnit, WialonUnitGroup
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.utils import get_id_from_iccid
from terminusgps_tracker.models.profile import TrackerProfile
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
)
from terminusgps_tracker.models.payment import TrackerPaymentMethod
from terminusgps_tracker.models.subscription import TrackerSubscription


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile.html"
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
        if request.user.is_authenticated:
            self.profile = TrackerProfile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Profile"
            context["profile"] = self.profile
            context["todos"] = self.profile.todo_list.items.all()
            context["subscription"] = self.profile.subscription or None
        return context


class TrackerProfileAssetView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_assets.html"
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
        if not request.session.get("wialon_session_id"):
            request.session["wialon_session_id"] = str(
                WialonSession().__enter__().wialon_api.sid
            )

        self.wialon_session_id = request.session["wialon_session_id"]
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_wialon_items(self, group_id: str) -> list[str]:
        wialon_group = WialonUnitGroup(
            id=group_id, session=WialonSession(sid=self.wialon_session_id)
        )
        return wialon_group.items

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Assets"
            context["wialon_items"] = self.get_wialon_items(
                group_id=str(self.profile.wialon_group_id)
            )
            print(context)
        return context


class TrackerProfileSubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_subscription.html"
    extra_context = {"title": "Your Subscription"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile and not self.profile.subscription:
            context["subtitle"] = "You haven't selected a subscription plan yet"
        elif self.profile:
            context["subtitle"] = (
                f"Thanks for subscribing! You're on the {self.profile.subscription.tier_display_gradient} plan"
            )
        return context


class TrackerProfileNotificationView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_notifications.html"
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
        try:
            self.profile = TrackerProfile.objects.get(user=request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Notifications"
        return context


class TrackerProfilePaymentMethodView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_payments.html"
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
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Payment Methods"
        return context


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
        else:
            # Complete the todo
            todo = self.profile.todo_list.items.filter(
                view__exact="profile create asset"
            )
            if todo.exists():
                todo_item = todo.first()
                todo_item.is_complete = True
                todo_item.save()
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

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if self.request.GET.get("tier"):
            initial["subscription_tier"] = self.request.GET.get("tier", "Cu")
        return initial

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: SubscriptionCreationForm) -> HttpResponse:
        if not self.profile.subscription:
            subscription_tier: str = form.cleaned_data["subscription_tier"]
            subscription_name: str = f"{self.profile.user.username}'s Subscription"
            subscription_duration: int = 12
            subscription = TrackerSubscription.objects.create(
                name=subscription_name,
                tier=subscription_tier,
                duration=subscription_duration,
            )
            self.profile.subscription = subscription
            self.profile.save()

        todo = self.profile.todo_list.items.filter(
            view__exact="profile create subscription"
        )
        if todo.exists():
            todo_item = todo.first()
            todo_item.is_complete = True
            todo_item.view = "tracker profile"
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
    success_url = reverse_lazy("profile payments")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form_cls = self.get_form_class()
        form = form_cls(request.POST)
        print(form)
        print(form.errors)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        request = self._generate_create_request(form)
        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            form.add_error(
                None,
                ValidationError(
                    _("Failed to create customer payment profile: %(error)s"),
                    code="invalid",
                    params={"error": response.messages.message["text"].text},
                ),
            )
            return self.form_invalid(form=form)

        if not self.profile.payments:
            self.profile.payments.set(
                [
                    TrackerPaymentMethod.objects.create(
                        id=int(response.customerPaymentProfileId), profile=self.profile
                    )
                ]
            )
        return super().form_valid(form=form)

    def _generate_create_request(self, form: PaymentMethodCreationForm):
        expirationDate = f"{form.cleaned_data["credit_card_expiry_month"]}-{form.cleaned_data["credit_card_expiry_year"]}"
        is_default = bool(form.cleaned_data["is_default"] == "on")
        return createCustomerPaymentProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(self.profile.authorizenet_profile_id),
            paymentProfile=customerPaymentProfileType(
                billTo=customerAddressType(
                    firstName=str(self.profile.user.first_name),
                    lastName=str(self.profile.user.last_name),
                    email=str(self.profile.user.username),
                    address=form.cleaned_data["address_street"],
                    city=form.cleaned_data["address_city"],
                    state=form.cleaned_data["address_state"],
                    zip=form.cleaned_data["address_zip"],
                    country=form.cleaned_data["address_country"],
                    phoneNumber=form.cleaned_data["address_phone"],
                ),
                payment=paymentType(
                    creditCard=creditCardType(
                        cardNumber=form.cleaned_data["credit_card_number"],
                        expirationDate=expirationDate,
                        cardCode=form.cleaned_data["credit_card_ccv"],
                    )
                ),
                defaultPaymentProfile=is_default,
            ),
            validationMode="liveMode" if not settings.DEBUG else "testMode",
        )


class TrackerProfilePaymentMethodDeletionView(LoginRequiredMixin, FormView):
    form_class = PaymentMethodDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_payment.html"
    extra_context = {
        "title": "Delete Payment Method",
        "subtitle": "Delete a payment method",
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
