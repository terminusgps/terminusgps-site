from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from terminusgps_tracker.http import HttpRequest
from terminusgps_tracker.models.customer import TrackerProfile
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
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Profile"
            context["profile"] = self.profile
            context["todo_list"] = self.profile.todo_list
            context["todos"] = self.profile.todo_list.items.all()
        if self.profile and self.profile.subscription:
            context["subscription"] = self.profile.subscription
            context["subscription_tier"] = self.profile.subscription.get_tier_display()
            context["subscription_gradient"] = (
                self.profile.subscription.tier_display_gradient
            )
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
        try:
            self.profile = TrackerProfile.objects.get(user=request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Assets"
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
        try:
            self.profile = TrackerProfile.objects.get(user=request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["subtitle"] = "You have not selected a subscription yet."
        elif self.profile and self.profile.subscription:
            context["subtitle"] = (
                f"Thanks for subscribing! You're on the {self.profile.subscription.tier_display_gradient} plan."
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
        try:
            self.profile = TrackerProfile.objects.get(user=request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

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


class TrackerProfileAssetDeletionView(LoginRequiredMixin, FormView):
    form_class = AssetDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_asset.html"
    extra_context = {"title": "New asset", "subtitle": "Register a new asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]


class TrackerProfileAssetModificationView(LoginRequiredMixin, FormView):
    form_class = AssetModificationForm
    template_name = "terminusgps_tracker/forms/profile/modify_asset.html"
    extra_context = {"title": "New asset", "subtitle": "Register a new asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]


class TrackerProfileSubscriptionCreationView(LoginRequiredMixin, FormView):
    form_class = SubscriptionCreationForm
    template_name = "terminusgps_tracker/forms/profile/create_subscription.html"
    extra_context = {"title": "New asset", "subtitle": "Register a new asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]


class TrackerProfileSubscriptionDeletionView(LoginRequiredMixin, FormView):
    form_class = SubscriptionDeletionForm
    template_name = "terminusgps_tracker/forms/profile/delete_subscription.html"
    extra_context = {"title": "Delete Asset", "subtitle": "Delete an asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]


class TrackerProfileSubscriptionModificationView(LoginRequiredMixin, FormView):
    form_class = SubscriptionModificationForm
    template_name = "terminusgps_tracker/forms/profile/modify_subscription.html"
    extra_context = {"title": "Modify Asset", "subtitle": "Modify an asset by IMEI #"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]


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
