import logging
import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import CreateView, DeleteView, ListView, TemplateView
from django.views.generic.base import ContextMixin
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerProfile

from .models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


class TerminusGPSCustomerContextMixin(ContextMixin):
    """Adds ``customer`` to the view context."""

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        try:
            context["customer"] = TerminusGPSCustomer.objects.get(
                user=self.request.user
            )
        except TerminusGPSCustomer.DoesNotExist:
            context["customer"] = None
        return context


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    template_name = "terminusgps_manager/account.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class DashboardView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Dashboard"}
    template_name = "terminusgps_manager/dashboard.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class UnitsView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Units"}
    template_name = "terminusgps_manager/units.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Subscription"}
    template_name = "terminusgps_manager/subscription.html"


class AuthorizenetProfileCreateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    CreateView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = None
    form_class = None
    success_url = reverse_lazy("terminusgps_manager:account")

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            obj = form.save(commit=False)
            obj.customer_profile = customer.customer_profile
            obj.save()
            return HttpResponseRedirect(self.get_success_url())
        except (
            TerminusGPSCustomer.DoesNotExist,
            CustomerProfile.DoesNotExist,
            AuthorizenetControllerExecutionError,
        ) as error:
            logger.warning(str(error))
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Something went wrong. Please try again later."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)


class AuthorizenetProfileListView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    ListView,
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = None
    ordering = "pk"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())


class AuthorizenetProfileDeleteView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    DeleteView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = None

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


class AuthorizenetProfileDeleteSuccessView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
