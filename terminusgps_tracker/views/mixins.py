import typing

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from terminusgps_tracker.models.customers import Customer
from terminusgps_tracker.models.subscriptions import CustomerSubscription

if not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class HtmxTemplateResponseMixin(TemplateResponseMixin):
    """
    Renders a partial HTML template depending on HTTP headers.

    `htmx documentation <https://htmx.org/docs/>`_

    """

    partial_template_name: str | None = None
    """
    A partial template rendered by `htmx`_.

    .. _htmx: https://htmx.org/docs/

    :type: :py:obj:`str` | :py:obj:`None`
    :value: :py:obj:`None`

    """

    def render_to_response(
        self, context: dict[str, typing.Any], **response_kwargs: typing.Any
    ) -> HttpResponse:
        htmx_request = self.request.headers.get("HX-Request", False)
        boosted = self.request.headers.get("HX-Boosted", False)

        if htmx_request and self.partial_template_name and not boosted:
            self.template_name = self.partial_template_name
        return super().render_to_response(context, **response_kwargs)


class TrackerAppConfigContextMixin(ContextMixin):
    """Adds the tracker app config to the view context."""

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["config"] = settings.TRACKER_APP_CONFIG
        return context


class CustomerRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("login")
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False

    def test_func(self) -> bool:
        if not hasattr(self, "request"):
            return False
        if not hasattr(self.request, "user"):
            return False
        if not self.request.user.is_authenticated:
            return False

        try:
            Customer.objects.get(user=self.request.user)
            return True
        except Customer.DoesNotExist:
            return False


class CustomerSubscriptionRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("login")
    permission_denied_message = (
        "An active subscription is required to perform this action."
    )
    raise_exception = False

    def test_func(self) -> bool:
        try:
            customer = Customer.objects.get(user=self.request.user)
            return (
                customer.subscription.status
                == CustomerSubscription.SubscriptionStatus.ACTIVE
            )
        except Customer.DoesNotExist:
            return False
