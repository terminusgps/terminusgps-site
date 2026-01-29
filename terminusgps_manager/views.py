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
from django.views.decorators.cache import cache_control, never_cache
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
from terminusgps.wialon.constants import ACCESSMASK_UNIT_BASIC
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps.wialon.utils import get_unit_from_imei
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
    Subscription,
)
from terminusgps_payments.tasks import sync_customer_profile

from .forms import (
    SubscriptionCreateForm,
    SubscriptionUpdateForm,
    WialonUnitCreateForm,
)
from .models import TerminusGPSCustomer, WialonUnit

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


@method_decorator(never_cache, name="dispatch")
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


@method_decorator(never_cache, name="dispatch")
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


@method_decorator(never_cache, name="dispatch")
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


@method_decorator(never_cache, name="dispatch")
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


@method_decorator(never_cache, name="dispatch")
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


@method_decorator(never_cache, name="dispatch")
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
            return super().form_valid(form=form)
        except (AuthorizenetControllerExecutionError, WialonAPIError) as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


@method_decorator(never_cache, name="dispatch")
class WialonUnitListView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    ListView,
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = WialonUnit
    ordering = "pk"
    paginate_by = 8
    template_name = "terminusgps_manager/units/list.html"

    def get_queryset(self) -> QuerySet:
        customer = TerminusGPSCustomer.objects.get(user=self.request.user)
        return customer.wialon_units.all().order_by(self.get_ordering())


@method_decorator(never_cache, name="dispatch")
class WialonUnitCreateView(
    LoginRequiredMixin,
    TerminusGPSCustomerContextMixin,
    HtmxTemplateResponseMixin,
    CreateView,
):
    content_type = "text/html"
    form_class = WialonUnitCreateForm
    http_method_names = ["get", "post"]
    model = WialonUnit
    template_name = "terminusgps_manager/units/create.html"
    success_url = reverse_lazy("terminusgps_manager:list units")

    @transaction.atomic
    def form_valid(self, form: WialonUnitCreateForm) -> HttpResponse:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            unit = WialonUnit()
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                data = get_unit_from_imei(form.cleaned_data["imei"], session)
                unit.pk = int(data["id"])
                unit.save()

                session.wialon_api.item_update_name(
                    **{"itemId": unit.pk, "name": form.cleaned_data["name"]}
                )
                customer.wialon_units.add(unit)
                customer.wialon_user.grant_access(
                    session, id=unit.pk, access_mask=ACCESSMASK_UNIT_BASIC
                )
                customer.save()
            return super().form_valid(form=form)
        except WialonAPIError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)
