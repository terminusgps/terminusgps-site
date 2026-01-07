import logging
import typing

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerProfile, Subscription

from .models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account", "subtitle": "Update your preferences"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/account.html#partial"
    template_name = "terminusgps_manager/account.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context


class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/dashboard.html#partial"
    template_name = "terminusgps_manager/dashboard.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context


class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/subscription.html#partial"
    template_name = "terminusgps_manager/subscription.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
            self.customer = TerminusGPSCustomer.objects.get(user=request.user)
        except (
            TerminusGPSCustomer.DoesNotExist,
            CustomerProfile.DoesNotExist,
        ):
            self.cprofile = None
            self.customer = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        context["customer"] = self.customer
        return context


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    fields = ["pprofile", "aprofile"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_manager/subscriptions/create.html#partial"
    )
    template_name = "terminusgps_manager/subscriptions/create.html"
    success_url = reverse_lazy("terminusgps_manager:subscriptions")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
            self.customer = TerminusGPSCustomer.objects.get(user=request.user)
        except (
            TerminusGPSCustomer.DoesNotExist,
            CustomerProfile.DoesNotExist,
        ):
            self.cprofile = None
            self.customer = None
        self.name = settings.SUBSCRIPTION_NAME
        self.amount = settings.SUBSCRIPTION_AMOUNT
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        context["customer"] = self.customer
        return context

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        payment_qs = self.cprofile.payment_profiles.all()
        address_qs = self.cprofile.address_profiles.all()
        form.fields["pprofile"].queryset = payment_qs
        form.fields["aprofile"].queryset = address_qs
        form.fields["pprofile"].empty_label = None
        form.fields["aprofile"].empty_label = None
        form.fields["pprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice payment profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        form.fields["aprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice address profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        return form

    @transaction.atomic
    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            sub = form.save(commit=False)
            sub.cprofile = self.cprofile
            sub.amount = self.amount
            sub.name = self.name
            sub.save()
            self.customer.subscription = sub
            self.customer.save(update_fields=["subscription"])
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            match error.code:
                case "E00012":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! A duplicate subscription already exists, nothing was created."
                            ),
                            code="invalid",
                            params={"error": error},
                        ),
                    )
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("Whoops! %(error)s"),
                            code="invalid",
                            params={"error": error},
                        ),
                    )
            return self.form_invalid(form=form)


class SubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/detail.html"
    partial_template_name = (
        "terminusgps_manager/subscriptions/detail.html#partial"
    )
    pk_url_kwarg = "subscription_pk"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["pprofile", "aprofile"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_manager/subscriptions/update.html#partial"
    )
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/update.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:detail subscriptions",
            kwargs={"subscription_pk": self.object.pk},
        )

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        payment_qs = self.cprofile.payment_profiles.all()
        address_qs = self.cprofile.address_profiles.all()
        form.fields["pprofile"].queryset = payment_qs
        form.fields["aprofile"].queryset = address_qs
        form.fields["pprofile"].empty_label = None
        form.fields["aprofile"].empty_label = None
        form.fields["pprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice payment profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        form.fields["aprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice address profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        return form


class SubscriptionCancelView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_manager/subscriptions/delete.html#partial"
    )
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/delete.html"
    success_url = reverse_lazy("terminusgps_manager:subscriptions")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"),
                    code="invalid",
                    params={"error": error},
                ),
            )
            return self.form_invalid(form=form)
