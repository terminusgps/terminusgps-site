from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView, FormView

from terminusgps_tracker.forms import TrackerRegistrationForm, TrackerAuthenticationForm
from terminusgps_tracker.models.subscription import TrackerSubscriptionTier


class TestTemplateView(TemplateView):
    template_name = "terminusgps_tracker/tooltip.html"
    content_type = "text/html"
    extra_context = {"element": "tooltip-logout", "text": "Logout"}
    http_method_names = ["get"]


class TrackerSubscriptionView(TemplateView):
    template_name = "terminusgps_tracker/subscriptions.html"
    content_type = "text/html"
    extra_context = {"title": "Subscriptions"}
    http_method_names = ["get"]

    def get_subscription_tiers(
        self, total: int = 3
    ) -> QuerySet[TrackerSubscriptionTier, TrackerSubscriptionTier | None]:
        queryset: QuerySet[TrackerSubscriptionTier, TrackerSubscriptionTier | None] = (
            TrackerSubscriptionTier.objects.all().order_by("amount")[:total]
        )
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription_tiers"] = self.get_subscription_tiers()
        return context


class TrackerAboutView(TemplateView):
    template_name = "terminusgps_tracker/about.html"
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]


class TrackerContactView(TemplateView):
    template_name = "terminusgps_tracker/contact.html"
    content_type = "text/html"
    extra_context = {
        "title": "Contact",
        "subtitle": "Ready to get in touch?",
        "profile": settings.TRACKER_PROFILE,
    }
    http_method_names = ["get"]


class TrackerPrivacyView(TemplateView):
    template_name = "terminusgps_tracker/privacy.html"
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy", "profile": settings.TRACKER_PROFILE}
    http_method_names = ["get"]


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_PROFILE["GITHUB"]


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/forms/login.html"


class TrackerLogoutView(SuccessMessageMixin, LogoutView):
    content_type = "text/html"
    template_name = "terminusgps_tracker/forms/logout.html"
    extra_context = {"title": "Logout"}
    success_url = reverse_lazy("tracker login")
    success_message = "You have been successfully logged out"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    http_method_names = ["get", "post", "options"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, *args, **kwargs)
        return HttpResponseRedirect(self.success_url)


class TrackerRegistrationView(SuccessMessageMixin, FormView):
    form_class = TrackerRegistrationForm
    content_type = "text/html"
    extra_context = {
        "title": "Registration",
        "subtitle": "Start tracking your vehicles with the Terminus GPS Tracker",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/register.html"
    success_url = reverse_lazy("tracker login")
    success_message = "%(username)s's account was created succesfully"

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_valid(self, form: TrackerRegistrationForm) -> HttpResponse:
        get_user_model().objects.create_user(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            email=form.cleaned_data["username"],
        )
        return super().form_valid(form=form)
