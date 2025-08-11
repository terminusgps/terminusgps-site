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
from terminusgps.authorizenet import subscriptions as anet_subscriptions
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
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
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        sub_total = customer.calculate_subscription_amount()

        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["sub_total"] = sub_total
        context["grand_total"] = calculate_amount_plus_tax(sub_total)
        context["start_date"] = customer.get_subscription_start_date()
        return context

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
            time_created = timezone.now()
            # Retrieve customer from db
            customer = Customer.objects.get(pk=self.kwargs["customer_pk"])

            # Generate subscription data
            subscription_name = f"{customer.user.first_name}'s Subscription"
            subscription_schedule = apicontractsv1.paymentScheduleType(
                interval=apicontractsv1.paymentScheduleTypeInterval(
                    length=1,
                    unit=apicontractsv1.ARBSubscriptionUnitEnum.months,
                ),
                startDate=time_created,
                totalOccurrences=9999,
                trialOccurrences=0,
            )
            subscription_profile = apicontractsv1.customerProfileIdType(
                customerProfileId=str(customer.authorizenet_profile_id),
                customerPaymentProfileId=str(form.cleaned_data["payment"].pk),
                customerAddressId=str(form.cleaned_data["address"].pk),
            )
            subscription_amount = calculate_amount_plus_tax(
                customer.calculate_subscription_amount()
            )

            # Create Authorizenet subscription
            response = anet_subscriptions.create_subscription(
                apicontractsv1.ARBSubscriptionType(
                    name=subscription_name,
                    amount=subscription_amount,
                    profile=subscription_profile,
                    paymentSchedule=subscription_schedule,
                    trialAmount=decimal.Decimal("0.00"),
                )
            )

            # Create local subscription
            local_sub = Subscription.objects.create(
                id=int(response.subscriptionId),
                name=subscription_name,
                payment=form.cleaned_data["payment"],
                address=form.cleaned_data["address"],
                customer=customer,
                start_date=time_created,
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

            # Send subscription confirmation email
            emails.send_subscription_created_email(customer, time_created)
            return HttpResponseRedirect(local_sub.get_absolute_url())
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
            # Retrieve subscription from db
            subscription = self.get_object()

            # Update Authorizenet subscription
            anet_subscriptions.update_subscription(
                subscription_id=subscription.pk,
                subscription_obj=apicontractsv1.ARBSubscriptionType(
                    profile=apicontractsv1.customerProfileIdType(
                        customerProfileId=str(
                            subscription.customer.authorizenet_profile_id
                        ),
                        customerPaymentProfileId=str(
                            form.cleaned_data["payment"].pk
                        ),
                        customerAddressId=str(form.cleaned_data["address"].pk),
                    )
                ),
            )

            # Update local subscription
            subscription.payment = form.cleaned_data["payment"]
            subscription.address = form.cleaned_data["address"]
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
        customer = subscription.customer
        cancel_date = timezone.now()
        anet_subscriptions.cancel_subscription(subscription.pk)

        with WialonSession() as session:
            account_id = customer.wialon_resource_id
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

        emails.send_subscription_canceled_email(customer, cancel_date)

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
