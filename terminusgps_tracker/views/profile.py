from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, View

from terminusgps.wialon.session import WialonSession

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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.profile and self.profile.assets.exists():
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


class TrackerProfilePaymentMethodCreationView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
    extra_context = {"title": "New Payment"}
    form_class = PaymentMethodCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/payments/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_message = "Payment method was added successfully."
    success_url = reverse_lazy("profile settings")
    template_name = "terminusgps_tracker/payments/create.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            return HttpResponse("", status=200)
        return HttpResponse(status=402)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(self.form_class)
        print(f"{form.is_bound = }")
        print(f"{form.is_valid() = }")
        print(f"{form.errors = }")
        return super().post(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

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
            return HttpResponse("", status=200)
        return HttpResponse(status=406)


class TrackerProfileShippingAddressCreationView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
    extra_context = {"title": "Create Shipping Address"}
    form_class = ShippingAddressCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_message = "Shipping address was added successfully."
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/addresses/create.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        return HttpResponse("", status=200)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

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
        return HttpResponse("", status=200)
