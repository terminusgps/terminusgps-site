import datetime
import logging
import typing

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.base import ContextMixin
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
    Subscription,
)
from terminusgps_payments.tasks import sync_customer_profile

from src.tasks import send_email

from .forms import SubscriptionCreateForm, SubscriptionUpdateForm
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


@method_decorator(cache_control(private=True), name="dispatch")
class TerminusGPSManagerTemplateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]


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
            obj = form.save(commit=False)
            obj.customer_profile = CustomerProfile.objects.get(
                user=self.request.user
            )
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


@method_decorator(cache_control(private=True), name="dispatch")
@method_decorator(cache_page(timeout=60 * 3), name="dispatch")
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


@method_decorator(cache_control(private=True), name="dispatch")
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


@method_decorator(cache_page(timeout=60 * 3), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionCreateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    CreateView,
):
    content_type = "text/html"
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/create.html"
    form_class = SubscriptionCreateForm

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        payment_qs = CustomerPaymentProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        address_qs = CustomerAddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].queryset = address_qs
        return form

    def form_valid(self, form: SubscriptionCreateForm) -> HttpResponse:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            customer_profile = CustomerProfile.objects.get(
                user=self.request.user
            )

            subscription = form.save(commit=False)
            subscription.start_date = datetime.date.today()
            subscription.customer_profile = customer_profile
            subscription.amount = customer.grand_total
            subscription.name = "Terminus GPS Subscription"
            subscription.save()
            customer.subscription = subscription
            customer.save(update_fields=["subscription"])
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                customer.wialon_account.enable(session)
                customer.wialon_account.update_flags(session, flags=-0x20)
            send_email.enqueue(
                to=[customer.user.email],
                subject="Terminus GPS - Subscription Created",
                template_name="terminusgps/emails/subscription_created.txt",
                html_template_name="terminusgps/emails/subscription_created.html",
                context={
                    "fn": customer.user.first_name,
                    "date": subscription.start_date.strftime("%Y-%m-%d"),
                },
            )
            return HttpResponseRedirect(
                reverse(
                    "terminusgps_manager:detail subscriptions",
                    kwargs={"pk": subscription.pk},
                )
            )
        except (
            TerminusGPSCustomer.DoesNotExist,
            CustomerProfile.DoesNotExist,
        ):
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Something went wrong. Please try again later."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


@method_decorator(cache_page(timeout=60 * 3), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionDetailView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


@method_decorator(cache_page(timeout=60 * 3), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionUpdateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    UpdateView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/update.html"
    form_class = SubscriptionUpdateForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer_profile = CustomerProfile.objects.get(user=request.user)
        sync_customer_profile(customer_profile.pk)
        return super().get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:detail subscriptions",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form: SubscriptionUpdateForm) -> HttpResponse:
        try:
            if any(
                [
                    "payment_profile" in form.changed_data,
                    "address_profile" in form.changed_data,
                ]
            ):
                return super().form_valid(form=form)
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        payment_qs = CustomerPaymentProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        address_qs = CustomerAddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].queryset = address_qs
        return form

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionDeleteView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    DeleteView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    success_url = reverse_lazy(
        "terminusgps_manager:delete subscriptions success"
    )
    template_name = "terminusgps_manager/subscriptions/delete.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        subscription = self.get_object()
        start_date = subscription.start_date
        end_date = datetime.date.today()
        customer = TerminusGPSCustomer.objects.get(user=self.request.user)
        service = AuthorizenetService()

        try:
            service.execute(
                api.cancel_subscription(subscription_id=self.get_object().pk)
            )
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                current_days = int(
                    session.wialon_api.account_get_account_data(
                        **{"itemId": customer.wialon_account.pk, "type": 2}
                    )["daysCounter"]
                )
                remaining_days = (end_date - start_date).days - current_days
                customer.wialon_account.enable(session)
                customer.wialon_account.do_payment(
                    session,
                    days=remaining_days,
                    desc=f"Canceled '{subscription.name}'. Added {remaining_days} days.",
                )
                customer.wialon_account.update_flags(session, flags=0x20)
                send_email.enqueue(
                    to=[customer.user.email],
                    subject="Terminus GPS - Subscription Canceled",
                    template_name="terminusgps/emails/subscription_canceled.txt",
                    html_template_name="terminusgps/emails/subscription_canceled.html",
                    context={
                        "fn": customer.user.first_name,
                        "date": end_date.strftime("%Y-%m-%d"),
                        "days": remaining_days,
                    },
                )
            return super().form_valid(form=form)
        except (AuthorizenetControllerExecutionError, WialonAPIError) as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)
