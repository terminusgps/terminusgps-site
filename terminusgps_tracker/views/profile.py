from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.dates import timezone_today

from terminusgps_tracker.forms.forms import SubscriptionSelectForm
from terminusgps_tracker.models.customer import TrackerProfile
from terminusgps_tracker.http import HttpRequest, HttpResponse
from terminusgps_tracker.models.subscription import TrackerSubscription


class TrackerProfilePaymentMethodsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/forms/profile_payments.html"
    extra_context = {
        "subtitle": "Create, update, or delete your payment methods",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self.profile.user.first_name}'s Payment Methods"
        return context


class TrackerProfileAssetsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/forms/profile_assets.html"
    extra_context = {
        "subtitle": "Register, modify, or delete your assets",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self.profile.user.first_name}'s Assets"
        return context


class TrackerProfileSubscriptionView(LoginRequiredMixin, FormView):
    form_class = SubscriptionSelectForm
    template_name = "terminusgps_tracker/forms/profile_subscription.html"
    extra_context = {
        "title": "Your Terminus GPS Subscription",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_initial(self, **kwargs) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial(**kwargs)
        initial["subscription"] = self.request.GET.get("tier", "Cu")
        return initial

    def form_valid(self, form: SubscriptionSelectForm) -> HttpResponse:
        if self.profile:
            new_subscription = TrackerSubscription.objects.get(
                tier=form.cleaned_data["subscription_tier"]
            )
            self.profile.subscription = new_subscription
            self.profile.save()
            print(self.profile.subscription)
        return super().form_valid(form=form)


class TrackerProfileNotificationsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/forms/profile_notifications.html"
    extra_context = {
        "title": "Your notifications",
        "subtitle": "Create, update, or delete your notifications",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile.html"
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
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        context["todos"] = self.profile.todo_list.items.all()
        return context
