import datetime
import logging
import typing

from django import forms
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
from terminusgps_payments.models import CustomerProfile, Subscription
from terminusgps_payments.tasks import sync_customer_profile_with_authorizenet

from .forms import SubscriptionForm
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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get("sync", "off") == "on":
            pk = CustomerProfile.objects.get(user=request.user).pk
            sync_customer_profile_with_authorizenet.enqueue(pk)
        return super().get(request, *args, **kwargs)

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


class SubscriptionCreateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    CreateView,
):
    content_type = "text/html"
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/create.html"
    form_class = SubscriptionForm

    def form_valid(self, form: SubscriptionForm) -> HttpResponse:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            obj = form.save(commit=False)
            obj.start_date = datetime.date.today()
            obj.customer_profile = customer.customer_profile
            obj.amount = customer.grand_total
            obj.name = "Terminus GPS Subscription"
            obj.save()
            customer.subscription = obj
            customer.save(update_fields=["subscription"])
            return HttpResponseRedirect(
                reverse(
                    "terminusgps_manager:detail subscriptions",
                    kwargs={"pk": obj.pk},
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
    form_class = SubscriptionForm

    def form_valid(self, form: SubscriptionForm) -> HttpResponse:
        try:
            print(f"{form.errors = }")
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


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

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            service = AuthorizenetService()
            service.execute(
                api.cancel_subscription(subscription_id=self.get_object().pk)
            )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


class SubscriptionDeleteSuccessView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_manager/subscriptions/delete_success.html"
