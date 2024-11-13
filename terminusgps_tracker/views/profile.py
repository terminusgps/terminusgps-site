from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from wialon.api import WialonError

from terminusgps_tracker.forms.forms import AssetUploadForm, SubscriptionSelectForm
from terminusgps_tracker.http import HttpRequest, HttpResponse
from terminusgps_tracker.integrations.wialon.items import WialonUnit, WialonUnitGroup
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.utils import get_id_from_iccid
from terminusgps_tracker.models.customer import TodoItem, TrackerProfile
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


class TrackerProfileAssetsView(LoginRequiredMixin, FormView):
    form_class = AssetUploadForm
    template_name = "terminusgps_tracker/forms/asset.html"
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
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Assets"
        return context

    def form_valid(self, form: AssetUploadForm) -> HttpResponse:
        try:
            self.asset_upload_flow(form)
        except WialonError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("Oops! Something went wrong on our end. Please try again later.")
                ),
            )
        except ValueError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("Oops! Something went wrong on our end. Please try again later.")
                ),
            )
        if self.profile.todo_list.items.filter(view__exact="profile assets").exists():
            todo = self.profile.todo_list.items.get(view__exact="profile assets")
            todo.is_complete = True
            todo.save()
        return super().form_valid(form=form)

    def get_unit(self, form: AssetUploadForm, session: WialonSession) -> WialonUnit:
        unit_id: str | None = get_id_from_iccid(
            form.cleaned_data["imei_number"], session=session
        )
        if not unit_id:
            raise ValueError(
                f"Could not locate unit by imei '{form.cleaned_data["imei_number"]}'"
            )
        return WialonUnit(id=unit_id, session=session)

    def asset_upload_flow(self, form: AssetUploadForm) -> None:
        with WialonSession() as session:
            unit = self.get_unit(form, session=session)
            available_group = WialonUnitGroup(id="27890571", session=session)
            user_group = WialonUnitGroup(
                id=str(self.profile.wialon_group_id), session=session
            )

            unit.rename(form.cleaned_data["asset_name"])
            user_group.add_item(unit)
            available_group.rm_item(unit)


class TrackerProfileSubscriptionView(LoginRequiredMixin, FormView):
    form_class = SubscriptionSelectForm
    template_name = "terminusgps_tracker/forms/profile_subscription.html"
    extra_context = {"legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"]}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.user:
            try:
                self.profile = TrackerProfile.objects.get(user=request.user)
            except TrackerProfile.DoesNotExist:
                self.profile = None

    def get_initial(self, **kwargs) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial(**kwargs)
        initial["subscription"] = self.request.GET.get("tier", "Cu")
        return initial

    def form_valid(self, form: SubscriptionSelectForm) -> HttpResponse:
        if self.profile:
            tier = form.cleaned_data["subscription_tier"]
            new_subscription = TrackerSubscription.objects.create(
                name=f"{self.profile.user.username}'s {tier} Subscription", tier=tier
            )
            self.profile.subscription = new_subscription
            if self.profile.todo_list.items.filter(
                view__exact="tracker subscriptions"
            ).exists():
                todo = self.profile.todo_list.items.get(
                    view__exact="tracker subscriptions"
                )
                todo.is_complete = True
                todo.save()
            self.profile.save()
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Subscription"

        if not self.profile or not self.profile.subscription:
            context["subtitle"] = "You haven't selected a subscription yet"
        else:
            context["subtitle"] = (
                f"You're currently on our {self.profile.subscription.tier_display} plan"
            )
        return context


class TrackerProfileNotificationsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/forms/profile_notifications.html"
    extra_context = {
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

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile:
            context["profile"] = self.profile
            context["title"] = f"{self.profile.user.first_name}'s Notifications"
            context["notifications"] = self.profile.notifications.all()
        return context


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
            context["todos"] = self.profile.todo_list.items.all()
            context["subscription_tier"] = self.profile.subscription.tier_display
            context["subscription_gradient"] = self.profile.subscription.tier_gradient
        return context
