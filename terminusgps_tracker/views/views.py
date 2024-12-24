from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, RedirectView, FormView

from terminusgps_tracker.forms import (
    TrackerSignupForm,
    TrackerAuthenticationForm,
    SubscriptionConfirmationForm,
)
from terminusgps_tracker.models import (
    TrackerProfile,
    TrackerSubscription,
    TrackerPaymentMethod,
    TrackerSubscriptionTier,
)


class TrackerLandingView(LoginRequiredMixin, RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = reverse_lazy("tracker profile")


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_PROFILE["GITHUB"]


class TrackerAboutView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/about.html"


class TrackerPrivacyView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy", "profile": settings.TRACKER_PROFILE}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/privacy.html"


class TrackerContactView(TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Contact",
        "subtitle": "Ready to get in touch?",
        "profile": settings.TRACKER_PROFILE,
    }
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/contact.html"


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/forms/login.html"


class TrackerLogoutView(SuccessMessageMixin, LogoutView):
    content_type = "text/html"
    template_name = "terminusgps_tracker/forms/logout.html"
    extra_context = {"title": "Logout"}
    success_url = reverse_lazy("tracker login")
    success_message = "You have been successfully logged out."
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    http_method_names = ["get", "post", "options"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, *args, **kwargs)
        return HttpResponseRedirect(self.success_url)


class TrackerSignupView(SuccessMessageMixin, FormView):
    form_class = TrackerSignupForm
    content_type = "text/html"
    extra_context = {"title": "Sign Up", "subtitle": "You'll know where yours are..."}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/signup.html"
    success_url = reverse_lazy("tracker login")
    success_message = "%(username)s's account was created succesfully"

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_valid(self, form: TrackerSignupForm) -> HttpResponse:
        user = get_user_model().objects.create_user(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            email=form.cleaned_data["username"],
        )
        profile = TrackerProfile.objects.create(user=user)
        TrackerSubscription.objects.create(profile=profile)
        return super().form_valid(form=form)


class TrackerSubscriptionOptionsView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Subscriptions"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/subscription_options.html"
    partial_name = "terminusgps_tracker/_subscription_options.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription_tiers"] = TrackerSubscriptionTier.objects.all()[:3]
        return context


class TrackerSubscriptionConfirmView(LoginRequiredMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Confirm Subscription"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/subscription_confirm.html"
    form_class = SubscriptionConfirmationForm
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    success_url = reverse_lazy("success subscription")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user.is_authenticated
            else None
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.profile is not None:
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
        if self.profile is not None:
            return {
                "payment_id": self.profile.payments.filter().first().authorizenet_id,
                "address_id": self.profile.addresses.filter().first().authorizenet_id,
            }
        return {}

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
            elif tier.amount < self.profile.tier.amount:
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
    template_name = "terminusgps_tracker/subscription_success.html"
    redirect_url = reverse_lazy("tracker profile")
