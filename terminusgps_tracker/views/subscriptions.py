import datetime
import decimal
import typing
from zoneinfo import ZoneInfo

from authorizenet import apicontractsv1
from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.profiles import SubscriptionProfile
from terminusgps.authorizenet.utils import (
    calculate_amount_plus_tax,
    get_transaction,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items import WialonResource
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.forms import SubscriptionCreationForm
from terminusgps_tracker.models import Customer, Subscription
from terminusgps_tracker.views.mixins import CustomerOrStaffRequiredMixin


class SubscriptionDetailView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    context_object_name = "subscription"
    http_method_names = ["get"]
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_detail.html"
    )
    pk_url_kwarg = "sub_pk"
    template_name = "terminusgps_tracker/subscriptions/detail.html"

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds the subscription start date to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["start_date"] = self.get_start_date()
        return context

    def get_start_date(self) -> datetime.datetime:
        """Retrieves the subscription start date from Authorizenet and returns it as an aware datetime."""
        return datetime.datetime.strptime(
            str(
                self.get_object()
                .authorizenet_get_subscription_profile()
                ._authorizenet_get_subscription()
                .find(f"{ANET_XMLNS}subscription")
                .find(f"{ANET_XMLNS}paymentSchedule")
                .find(f"{ANET_XMLNS}startDate")
            ),
            "%Y-%m-%d",
        ).replace(hour=2, tzinfo=ZoneInfo("US/Pacific"))


class SubscriptionCreateView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    FormView,
):
    content_type = "text/html"
    form_class = SubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_create.html"
    )
    template_name = "terminusgps_tracker/subscriptions/create.html"

    def get_success_url(self) -> str:
        return Customer.objects.get(
            pk=self.kwargs["customer_pk"]
        ).subscription.get_absolute_url()

    def get_form(
        self, form_class: SubscriptionCreationForm | None = None
    ) -> SubscriptionCreationForm:
        form = super().get_form(form_class=form_class)
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])

        form.fields["address"].queryset = customer.addresses.all()
        form.fields["address"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "tracker:address choices",
                    kwargs={"customer_pk": customer.pk},
                )
            }
        )

        form.fields["payment"].queryset = customer.payments.all()
        form.fields["payment"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "tracker:payment choices",
                    kwargs={"customer_pk": customer.pk},
                )
            }
        )
        return form

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(
            pk=self.kwargs["customer_pk"]
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])

        if customer.units.count() == 0:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Please register a unit before subscribing."),
                    code="invalid",
                ),
            )
        if not customer.wialon_resource_id:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! You don't have a Wialon account assigned."),
                    code="invalid",
                ),
            )

        return (
            self.form_valid(form=form)
            if form.is_valid()
            else self.form_invalid(form=form)
        )

    def form_valid(
        self, form: SubscriptionCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            # Generate subscription data
            customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
            subscription_name = self.generate_subscription_name(customer)
            anet_subscription_obj = apicontractsv1.ARBSubscriptionType(
                name=subscription_name,
                amount=self.generate_subscription_amount(customer),
                profile=self.generate_customer_profile(customer, form),
                paymentSchedule=self.generate_subscription_schedule(),
                trialAmount=decimal.Decimal(0.00),
            )

            # Create Authorizenet subscription
            anet_profile = SubscriptionProfile(
                customer_profile_id=customer.authorizenet_profile_id, id=None
            )
            subscription_id = anet_profile.create(anet_subscription_obj)

            # Create local subscription
            Subscription.objects.create(
                id=subscription_id,
                name=subscription_name,
                payment=form.cleaned_data["payment"],
                address=form.cleaned_data["address"],
                customer=customer,
            )
            self.wialon_add_days_to_account(
                customer, relativedelta(timezone.now(), months=1).days
            )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! '%(e)s'"), code="invalid", params={"e": e}
                ),
            )
            return self.form_invalid(form=form)
        except ValueError as e:
            form.add_error(
                None,
                ValidationError(
                    _("ValueError! '%(e)s'"), code="invalid", params={"e": e}
                ),
            )
            return self.form_invalid(form=form)

    @staticmethod
    def generate_customer_profile(
        customer: Customer, form: SubscriptionCreationForm
    ) -> apicontractsv1.customerProfileIdType:
        """
        Returns an Authorizenet customer profile based on the customer and form.

        :param customer: A customer to generate a profile for.
        :type customer: :py:obj:`~terminusgps_tracker.models.customers.Customer`
        :param form: A subscription creation form.
        :type form: :py:obj:`~terminusgps_tracker.forms.subscriptions.SubscriptionCreationForm`
        :returns: An Authorizenet customer profile (ID type).
        :rtype: :py:obj:`~authorizenet.apicontractsv1.customerProfileIdType`

        """
        return apicontractsv1.customerProfileIdType(
            customerProfileId=str(customer.authorizenet_profile_id),
            customerPaymentProfileId=str(form.cleaned_data["payment"].pk),
            customerAddressId=str(form.cleaned_data["address"].pk),
        )

    @staticmethod
    def generate_subscription_name(customer: Customer) -> str:
        """
        Returns a subscription name based the customer.

        :param customer: A customer to generate a subscription name based on.
        :type customer: :py:obj:`~terminusgps_tracker.models.customers.Customer`
        :returns: A subscription name.
        :rtype: :py:obj:`str`

        """
        return f"{customer.user.first_name}'s Subscription"

    @staticmethod
    def generate_subscription_schedule(
        trial_months: int = 0,
    ) -> apicontractsv1.paymentScheduleType:
        """
        Returns an Authorizenet payment schedule for a subscription.

        :param trial_months: Number of free months to grant to the customer. Default is ``0``.
        :type trial_months: :py:obj:`int`
        :returns: A payment schedule object for Authorizenet API calls.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentScheduleType`

        """
        return apicontractsv1.paymentScheduleType(
            interval=apicontractsv1.paymentScheduleTypeInterval(
                length=1, unit=apicontractsv1.ARBSubscriptionUnitEnum.months
            ),
            startDate=timezone.now(),
            totalOccurrences=9999,
            trialOccurrences=trial_months,
        )

    @staticmethod
    def generate_subscription_amount(
        customer: Customer, add_tax: bool = True
    ) -> decimal.Decimal:
        """
        Returns an amount to be charged for a subscription based on the customer.

        :param customer: A customer to calculate a subscription amount for.
        :type customer: :py:obj:`~terminusgps_tracker.models.customers.Customer`
        :param add_tax: Whether or not to add tax to the subscription amount. Default is :py:obj:`True`.
        :type add_tax: :py:obj:`bool`
        :raises ValueError: If the customer doesn't have any units to generate an amount with.
        :returns: An amount for a subscription.
        :rtype: :py:obj:`~decimal.Decimal`

        """
        raw_amount = customer.get_unit_amounts()
        if raw_amount is None:
            raise ValueError(
                f"Failed to retrieve unit amounts for {customer}."
            )
        return calculate_amount_plus_tax(raw_amount) if add_tax else raw_amount

    @staticmethod
    def wialon_add_days_to_account(
        customer: Customer, num_days: int
    ) -> Customer:
        """
        Adds ``num_days`` to the customer's Wialon account and returns the customer.

        :param customer: A customer whose account will have days added.
        :type customer: :py:obj:`~terminusgps_tracker.models.customers.Customer`
        :param num_days: Number of days to add to the Wialon account.
        :type num_days: :py:obj:`int`
        :returns: The customer.
        :rtype: :py:obj:`~terminusgps_tracker.models.customers.Customer`

        """
        with WialonSession() as session:
            resource = WialonResource(customer.wialon_resource_id, session)
            resource.add_days(num_days)
        return customer


class SubscriptionUpdateView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    UpdateView,
):
    content_type = "text/html"
    fields = ["payment", "address", "features"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_update.html"
    )
    pk_url_kwarg = "sub_pk"
    template_name = "terminusgps_tracker/subscriptions/update.html"

    def form_valid(
        self, form: forms.Form
    ) -> HttpResponse | HttpResponseRedirect:
        response = super().form_valid(form=form)
        subscription = self.get_object()
        sprofile = subscription.authorizenet_get_subscription_profile()
        subscription.authorizenet_update_amount(sprofile)
        subscription.authorizenet_update_payment(sprofile)
        subscription.save()
        return response

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])

        form.fields["address"].queryset = customer.addresses.all()
        form.fields["address"].widget.attrs.update(
            {
                "class": settings.DEFAULT_FIELD_CLASS,
                "hx-target": "this",
                "hx-trigger": "load",
                "hx-get": reverse(
                    "tracker:address choices",
                    kwargs={"customer_pk": customer.pk},
                ),
            }
        )

        form.fields["payment"].queryset = customer.payments.all()
        form.fields["payment"].widget.attrs.update(
            {
                "class": settings.DEFAULT_FIELD_CLASS,
                "hx-target": "this",
                "hx-trigger": "load",
                "hx-get": reverse(
                    "tracker:payment choices",
                    kwargs={"customer_pk": customer.pk},
                ),
            }
        )
        form.fields["features"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["features"].label = "Additional Features"
        form.fields[
            "features"
        ].help_text = "Ctrl+click to select multiple. Cmd+click on Mac."
        return form


class SubscriptionDeleteView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DeleteView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_delete.html"
    )
    pk_url_kwarg = "sub_pk"
    template_name = "terminusgps_tracker/subscriptions/delete.html"
    success_url = reverse_lazy("tracker:subscription")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        subscription = self.get_object()
        sprofile = subscription.authorizenet_get_subscription_profile()
        sprofile.delete()
        return super().post(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )


class SubscriptionTransactionsView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    context_object_name = "subscription"
    http_method_names = ["get"]
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_transactions.html"
    )
    pk_url_kwarg = "sub_pk"
    template_name = "terminusgps_tracker/subscriptions/transactions.html"

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        subscription = self.get_object()
        context["transaction_list"] = (
            subscription.authorizenet_get_transaction_list(
                subscription.authorizenet_get_subscription_profile()
            )
        )
        return context


class SubscriptionTransactionDetailView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/subscriptions/transaction_detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_transaction_detail.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if self.kwargs.get("transaction_id"):
            trans_id = self.kwargs["transaction_id"]
            trans_obj = get_transaction(trans_id).transaction
            context["transaction"] = trans_obj
            context["submit_time"] = datetime.datetime.strptime(
                str(trans_obj.submitTimeUTC), "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        return context


class SubscriptionItemListView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_items.html"
    )
    template_name = "terminusgps_tracker/subscriptions/items.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        subscription = Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).get(pk=self.kwargs["sub_pk"])
        context["items_list"] = list(subscription.customer.units.all())
        context["items_list"].extend(list(subscription.features.all()))
        return context
