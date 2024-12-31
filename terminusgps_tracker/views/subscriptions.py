from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, FormView, UpdateView

from terminusgps_tracker.forms import SubscriptionConfirmationForm
from terminusgps_tracker.models import (
    TrackerProfile,
    TrackerSubscription,
    TrackerSubscriptionTier,
    TrackerPaymentMethod,
)


class TrackerSubscriptionOptionsView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Subscriptions"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/subscriptions/options.html"
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_options.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.tiers = TrackerSubscriptionTier.objects.filter()[:3]
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription_tiers"] = self.tiers
        return context


class TrackerSubscriptionConfirmView(LoginRequiredMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Confirm Subscription"}
    form_class = SubscriptionConfirmationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_confirm.html"
    permission_denied_message = "Please login and try again."
    raise_exception = False
    success_url = reverse_lazy("success subscription")
    template_name = "terminusgps_tracker/subscriptions/confirm.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user.is_authenticated
            else None
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.profile:
            if self.profile.payments.count() == 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Please add a payment method before proceeding.",
                )
                return HttpResponseRedirect(reverse("profile settings"))
            if self.profile.addresses.count() == 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Please add a shipping address before proceeding.",
                )
                return HttpResponseRedirect(reverse("profile settings"))
        return super().get(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        if not self.profile:
            return {}
        return {
            "payment_id": self.profile.payments.filter().first().authorizenet_id,
            "address_id": self.profile.addresses.filter().first().authorizenet_id,
        }

    def form_valid(self, form: SubscriptionConfirmationForm) -> HttpResponse:
        new_tier: TrackerSubscriptionTier = TrackerSubscriptionTier.objects.get(
            pk=self.kwargs["tier"]
        )
        try:
            if (
                self.profile.subscription.tier is None
                or new_tier.amount > self.profile.subscription.tier.amount
            ):
                self.profile.subscription.upgrade(
                    new_tier,
                    int(form.cleaned_data["payment_id"]),
                    int(form.cleaned_data["address_id"]),
                )
            elif new_tier.amount < self.profile.tier.amount:
                self.profile.subscription.downgrade(
                    new_tier,
                    int(form.cleaned_data["payment_id"]),
                    int(form.cleaned_data["address_id"]),
                )
        except ValueError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        except AssertionError:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Couldn't find a payment method and a shipping address."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["tier"] = TrackerSubscriptionTier.objects.get(pk=self.kwargs["tier"])
        context["now"] = timezone.now()
        if self.profile is not None:
            payment = TrackerPaymentMethod.authorizenet_get_payment_profile(
                profile_id=self.profile.authorizenet_id,
                payment_id=self.get_initial()["payment_id"],
            )
            context["card_last_4"] = payment["payment"]["creditCard"]["cardNumber"]
            context["card_merchant"] = payment["payment"]["creditCard"]["cardType"]
        return context


class TrackerSubscriptionSuccessView(LoginRequiredMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Successfully Subscribed!",
        "subtitle": "Thanks for subscribing!",
    }
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_success.html"
    permission_denied_message = "Please login and try again."
    raise_exception = False
    redirect_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/subscriptions/success.html"
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_success.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name


class TrackerSubscriptionUpdateView(LoginRequiredMixin, UpdateView):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = None
    fields = ["id", "tier", "payment_id", "address_id"]
    model = TrackerSubscription
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/subscriptions/update.html"
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_update.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

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
