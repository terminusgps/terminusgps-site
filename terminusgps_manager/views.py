import logging
import typing

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ngettext
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps_payments.models import Subscription
from terminusgps_payments.views.generic import AuthorizenetDeleteView
from terminusgps_payments.views.subscriptions import SubscriptionCreateView

from .models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


class TerminusGPSCustomerContextMixin(ContextMixin):
    """Adds ``customer`` to the view context."""

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
        except TerminusGPSCustomer.DoesNotExist:
            customer = None

        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = customer
        return context


@method_decorator(cache_control(private=True), name="dispatch")
class TerminusGPSManagerTemplateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]


class SubscriptionCreateSuccessView(TerminusGPSManagerTemplateView):
    template_name = "terminusgps_payments/subscription_create_success.html"


class TerminusGPSManagerSubscriptionDeleteView(AuthorizenetDeleteView):
    model = Subscription

    def get_success_url(self) -> str:
        return reverse("terminusgps_manager:create subscriptions")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            start_date = customer.subscription.start_date
            end_date = start_date + relativedelta(months=1)
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                resp = customer.wialon_account.get_account_data(session)
                curr = int(resp["daysCounter"])
                days = (end_date - start_date).days - curr
                customer.wialon_account.enable(session)
                customer.wialon_account.update_flags(session, flags=0x20)
                customer.wialon_account.do_payment(
                    session,
                    days=days,
                    desc=f"terminusgps_manager: Added {days} {ngettext('day', 'days', days)}.",
                )
            super().form_valid(form=form)
            return HttpResponseRedirect(self.get_success_url())
        except (TerminusGPSCustomer.DoesNotExist, WialonAPIError) as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": error}
                ),
            )
            return self.form_invalid(form=form)


class TerminusGPSManagerSubscriptionCreateView(SubscriptionCreateView):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.customer = (
                TerminusGPSCustomer.objects.get(user=request.user)
                if hasattr(request, "user")
                else None
            )
            self.amount = self.customer.grand_total
        except TerminusGPSCustomer.DoesNotExist:
            self.customer = None

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        sub_total = (
            self.customer.sub_total if self.customer is not None else None
        )
        tax_total = (
            self.customer.tax_total if self.customer is not None else None
        )
        grand_total = (
            self.customer.grand_total if self.customer is not None else None
        )

        context = super().get_context_data(**kwargs)
        context["sub_total"] = sub_total
        context["tax_total"] = tax_total
        context["grand_total"] = grand_total
        return context

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            response = super().form_valid(form=form)
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            customer.subscription = self.object
            customer.save(update_fields=["subscription"])
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                customer.wialon_account.enable(session)
                customer.wialon_account.update_flags(session, flags=-0x20)
            return response
        except (TerminusGPSCustomer.DoesNotExist, WialonAPIError):
            return response
