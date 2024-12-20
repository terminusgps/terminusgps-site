from typing import Any

from django.conf import settings
from django.forms import Form
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView, View

from terminusgps_tracker.forms import (
    PaymentMethodCreationForm,
    ShippingAddressCreationForm,
)
from terminusgps_tracker.models import (
    TrackerPaymentMethod,
    TrackerProfile,
    TrackerShippingAddress,
    TrackerSubscription,
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
        self.profile = None
        if request.user.is_authenticated:
            self.profile, _ = TrackerProfile.objects.get_or_create(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["assets"] = self.get_assets(self.profile)
        context["subscription"], _ = TrackerSubscription.objects.get_or_create(
            profile=self.profile
        )
        return context

    @staticmethod
    def get_assets(profile: TrackerProfile | None = None) -> QuerySet | None:
        if not profile or not profile.assets.filter().exists():
            return
        return profile.assets.all()


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
            for payment in profile.payments.all()[:total]
        ]

    @staticmethod
    def get_addresses(profile: TrackerProfile, total: int = 4) -> list:
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
            for address in profile.addresses.all()[:total]
        ]


class TrackerProfilePaymentMethodCreationView(LoginRequiredMixin, FormView):
    form_class = PaymentMethodCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_payment.html"
    partial_template = "terminusgps_tracker/forms/settings/create_payment.html"
    extra_context = {"title": "New Payment"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
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


class TrackerProfileShippingAddressCreationView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_shipping_address.html"
    partial_template = "terminusgps_tracker/forms/settings/create_address.html"
    extra_context = {"title": "Create Shipping Address"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
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


class TrackerProfileSubscriptionModificationView(LoginRequiredMixin, UpdateView):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = None
    fields = ["id", "tier", "payment_id", "address_id"]
    model = TrackerSubscription
    template_name = "terminusgps_tracker/forms/profile/modify_subscription.html"
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def form_valid(self, form: Form) -> HttpResponse:
        subscription = self.get_object()
        curr_tier = subscription.tier
        new_tier = form.cleaned_data["tier"]
        if curr_tier is None or curr_tier.amount < new_tier.amount:
            subscription.upgrade(
                new_tier,
                form.cleaned_data.get("payment_id"),
                form.cleaned_data.get("address_id"),
            )
        else:
            subscription.downgrade(
                new_tier,
                form.cleaned_data.get("payment_id"),
                form.cleaned_data.get("address_id"),
            )
        return super().form_valid(form)

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        if self.profile.payments.filter().exists():
            initial["payment_id"] = (
                self.profile.payments.filter(is_default=True).first().authorizenet_id
            )
        if self.profile.addresses.filter().exists():
            initial["address_id"] = (
                self.profile.addresses.filter(is_default=True).first().authorizenet_id
            )
        return initial
