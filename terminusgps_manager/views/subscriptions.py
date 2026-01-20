import logging
import typing

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps_payments.models import CustomerProfile, Subscription

from ..forms import SubscriptionCreateForm
from ..models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    form_class = SubscriptionCreateForm
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )
        self.cprofile, _ = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = self.cprofile
        return context

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        form.fields["pprofile"].queryset = self.cprofile.payment_profiles.all()
        form.fields["aprofile"].queryset = self.cprofile.address_profiles.all()
        return form

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            sub = form.save(commit=False)
            sub.name = "Terminus GPS Subscription"
            sub.amount = self.customer.grand_total
            sub.cprofile = self.cprofile
            sub.save()

            self.customer.subscription = sub
            self.customer.save(update_fields=["subscription"])
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                self.customer.wialon_account.update_flags(session, flags=-0x20)
                self.customer.wialon_account.enable(session)
            return HttpResponseRedirect(
                reverse(
                    "terminusgps_manager:detail subscriptions",
                    kwargs={"subscription_pk": sub.pk},
                )
            )
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    _("%(error)s"),
                    code="invalid",
                    params={"error": str(error)},
                ),
            )
            return self.form_invalid(form=form)
        except WialonAPIError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


class SubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/detail.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            obj = self.get_object()
            resp = obj.get_from_authorizenet(AuthorizenetService())
            obj.status = str(resp.subscription.status)
            obj.save(update_fields=["status"])
            return super().get(request, *args, **kwargs)
        except AuthorizenetControllerExecutionError as error:
            logger.warning(error)
            return super().get(request, *args, **kwargs)


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["aprofile", "pprofile"]
    http_method_names = ["get", "post"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/update.html"

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        cprofile, _ = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        form.fields["pprofile"].queryset = cprofile.payment_profiles.all()
        form.fields["pprofile"].empty_label = None
        form.fields["aprofile"].queryset = cprofile.address_profiles.all()
        form.fields["aprofile"].empty_label = None
        return form

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:detail subscriptions",
            kwargs={"subscription_pk": self.object.pk},
        )


class SubscriptionDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["post"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    success_url = reverse_lazy("terminusgps_manager:create subscriptions")

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            start_date = self.object.start_date
            end_date = start_date + relativedelta(months=1)
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            customer.end_date = end_date
            customer.save(update_fields=["end_date"])
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                curr_days = int(
                    customer.wialon_account.get_account_data(
                        session, response_type=1
                    )["daysCounter"]
                )
                customer.wialon_account.do_payment(
                    session,
                    days=(end_date - start_date).days - curr_days,
                    desc=f"Canceled '{self.object.name}'.",
                )
                customer.wialon_account.update_flags(session, flags=0x20)
            return super().form_valid(form=form)
        except (AuthorizenetControllerExecutionError, WialonAPIError) as error:
            logger.warning(error)
            return HttpResponse(status=406)


class SubscriptionTransactionsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/transactions.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)

        try:
            context["arbTransactions"] = getattr(
                self.object.get_from_authorizenet(
                    AuthorizenetService(), include_transactions=True
                ).subscription,
                "arbTransactions",
                [],
            )
            return context
        except AuthorizenetControllerExecutionError as error:
            logger.warning(error)
            context["arbTransactions"] = []
            return context
