import datetime
import decimal
import typing

from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.profiles import SubscriptionProfile
from terminusgps.authorizenet.utils import (
    calculate_amount_plus_tax,
    get_transaction,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.forms import SubscriptionCreationForm
from terminusgps_tracker.models import (
    Customer,
    CustomerWialonUnit,
    Subscription,
)
from terminusgps_tracker.views.mixins import CustomerOrStaffRequiredMixin

from .. import emails


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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds ``grand_total`` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["grand_total"] = self.get_object().calculate_amount()
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Syncs the subscription's data with Authorizenet if necessary."""
        subscription = self.get_object()
        if subscription.authorizenet_needs_sync():
            subscription.authorizenet_sync()
            subscription.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")


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

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        initial["payment"] = customer.payments.first()
        initial["address"] = customer.addresses.first()
        return initial

    def get_form(self, form_class=None) -> SubscriptionCreationForm:
        """Sets customer payment/address choices for the form."""
        form = super().get_form(form_class=form_class)
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        form.fields["payment"].queryset = customer.payments.all()
        form.fields["address"].queryset = customer.addresses.all()
        return form

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(
            pk=self.kwargs["customer_pk"]
        )
        return context

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
            subscription_id = SubscriptionProfile(
                customer_profile_id=customer.authorizenet_profile_id
            ).create(anet_subscription_obj)

            # Create local subscription
            sub = Subscription.objects.create(
                id=subscription_id,
                name=subscription_name,
                payment=form.cleaned_data["payment"],
                address=form.cleaned_data["address"],
                customer=customer,
            )
            # Enable Wialon account
            with WialonSession() as session:
                account_id = customer.wialon_resource_id
                session.wialon_api.account_update_flags(
                    **{"itemId": account_id, "flags": -0x20}
                )
                session.wialon_api.account_enable_account(
                    **{"itemId": account_id, "enable": int(True)}
                )
            emails.send_subscription_created_email(customer, timezone.now())
            return HttpResponseRedirect(sub.get_absolute_url())
        except ValueError:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! You can't subscribe without any units."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        except AuthorizenetControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! '%(e)s'"), code="invalid", params={"e": e}
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
        :raises ValueError: If the customer didn't have any units.
        :returns: An amount for a subscription.
        :rtype: :py:obj:`~decimal.Decimal`

        """
        unit_qs = CustomerWialonUnit.objects.filter(customer=customer)
        if unit_qs.count() == 0:
            raise ValueError("Customer doesn't have any units.")

        raw_amount = sum(
            unit_qs.values_list("tier__amount", flat=True),
            decimal.Decimal("0.00"),
        )
        return calculate_amount_plus_tax(raw_amount) if add_tax else raw_amount


class SubscriptionUpdateView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    UpdateView,
):
    content_type = "text/html"
    fields = ["payment", "address"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_update.html"
    )
    pk_url_kwarg = "sub_pk"
    template_name = "terminusgps_tracker/subscriptions/update.html"

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def form_valid(
        self, form: forms.Form
    ) -> HttpResponse | HttpResponseRedirect:
        """Updates the subscription's payment method and shipping address in Authorizenet."""
        try:
            subscription = self.get_object()
            sprofile = subscription._authorizenet_get_profile()
            subscription.authorizenet_update_payment(sprofile)
            subscription.save()
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(e)s."),
                    code="invalid",
                    params={"e": e.message},
                ),
            )
            return self.form_invalid(form=form)

    def get_form(self, form_class=None):
        """Styles and sets customer payment/address choices for the form."""
        form = super().get_form(form_class=form_class)
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        form.fields["payment"].empty_label = None
        form.fields["payment"].queryset = customer.payments.all()
        form.fields["payment"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["address"].empty_label = None
        form.fields["address"].queryset = customer.addresses.all()
        form.fields["address"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
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
    success_url = reverse_lazy("tracker:subscription")
    template_name = "terminusgps_tracker/subscriptions/delete.html"

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds ``remaining_days`` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["remaining_days"] = self.get_object().get_remaining_days()
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Deletes the Authorizenet subscription and adds remaining days to the customer's Wialon account."""
        subscription = self.get_object()
        sprofile = subscription._authorizenet_get_profile()
        sprofile.delete()

        with WialonSession() as session:
            account_id = subscription.customer.wialon_resource_id
            remaining_days = subscription.get_remaining_days()

            session.wialon_api.account_update_flags(
                **{"itemId": account_id, "flags": 0x20}
            )
            session.wialon_api.account_do_payment(
                **{
                    "itemId": account_id,
                    "daysUpdate": remaining_days,
                    "balanceUpdate": "0.00",
                    "description": f"Canceled {subscription}.",
                }
            )

        emails.send_subscription_canceled_email(
            self.get_object().customer, timezone.now()
        )
        # Retarget required otherwise the response is nested for some reason
        response = super().post(request, *args, **kwargs)
        response.headers["HX-Retarget"] = "#subscription"
        return response


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
        context["transaction_list"] = (
            self.get_object().authorizenet_get_transaction_list()
        )
        return context


class SubscriptionTransactionDetailView(
    HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_transaction_detail.html"
    )
    template_name = "terminusgps_tracker/subscriptions/transaction_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds ``transaction`` and ``submit_time`` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if self.kwargs.get("transaction_id"):
            trans_id = self.kwargs["transaction_id"]
            trans_obj = get_transaction(trans_id).transaction
            context["transaction"] = trans_obj
            context["submit_time"] = datetime.datetime.strptime(
                str(trans_obj.submitTimeUTC), "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        return context


class SubscriptionItemListView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_item_list.html"
    )
    template_name = "terminusgps_tracker/subscriptions/item_list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            Subscription.objects.filter(
                customer__pk=self.kwargs.get("customer_pk")
            ).get(pk=self.kwargs.get("sub_pk"))
            return super().get(request, *args, **kwargs)
        except (Customer.DoesNotExist, Subscription.DoesNotExist):
            return HttpResponse(status=404)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        context["items_list"] = CustomerWialonUnit.objects.filter(
            customer=customer
        )
        return context
