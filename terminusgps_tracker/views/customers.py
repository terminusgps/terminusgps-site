import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, TemplateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants as wialon_constants
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonResource, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.forms import CustomerWialonUnitCreationForm
from terminusgps_tracker.models import (
    Customer,
    CustomerWialonUnit,
    Subscription,
)


class CustomerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": settings.TRACKER_APP_CONFIG["MOTD"],
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/dashboard.html"


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Account",
        "subtitle": "Update your payment information",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_account.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/account.html"


class CustomerSubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Your Subscription",
        "subtitle": "Update your subscription plan",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_subscription.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscription.html"


class CustomerTransactionsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Transactions",
        "subtitle": "Inspect your subscription transactions",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_transactions.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/transactions.html"


class CustomerSupportView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Support",
        "subtitle": "Drop us a line and we'll get in touch",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_support.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/support.html"


class CustomerWialonUnitsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Units",
        "subtitle": "Your currently active units",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_units.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/units.html"


class CustomerWialonUnitDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Unit Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerWialonUnit.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/units/detail.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        """Retrieves associated Wialon units for the customer."""
        return CustomerWialonUnit.objects.filter(
            customer__user=self.request.user
        ).select_related("customer")


class CustomerWialonUnitListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "unit_list"
    extra_context = {"title": "Unit List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    ordering = "name"
    partial_template_name = "terminusgps_tracker/units/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerWialonUnit.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/units/list.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        """Retrieves associated Wialon units for the customer."""
        return (
            CustomerWialonUnit.objects.filter(customer__user=self.request.user)
            .select_related("customer")
            .order_by(self.get_ordering())
        )


class CustomerWialonUnitCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Unit"}
    form_class = CustomerWialonUnitCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/units/partials/_create.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("tracker:units")
    template_name = "terminusgps_tracker/units/create.html"

    def wialon_unit_exists(self, imei_number: str) -> bool:
        """Checks if a Wialon unit exists by imei number."""
        with WialonSession() as session:
            return bool(
                wialon_utils.get_unit_by_imei(
                    imei=imei_number, session=session
                )
            )

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["name"] = f"{self.request.user.first_name}'s Ride"
        initial["imei"] = self.request.GET.get("imei")
        return initial

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Validates the form data before doing anything with the Wialon API."""
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form=form)

        customer = Customer.objects.get(user=request.user)
        if not self.wialon_unit_exists(form.cleaned_data["imei"]):
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! There's no Wialon unit with IMEI # '%(imei_number)s'. Please try again later."
                    ),
                    code="invalid",
                    params={"imei_number": form.cleaned_data["imei"]},
                ),
            )
        if not customer.wialon_resource_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! There's no Wialon account associated with '%(email)s'. Please try again later."
                    ),
                    code="invalid",
                    params={
                        "email": customer.user.email
                        if customer.user.email
                        else customer.user.username
                    },
                ),
            )
        if not customer.wialon_user_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! There's no Wialon user associated with '%(email)s'. Please try again later."
                    ),
                    code="invalid",
                    params={
                        "email": customer.user.email
                        if customer.user.email
                        else customer.user.username
                    },
                ),
            )

        return (
            self.form_valid(form=form)
            if form.is_valid()
            else self.form_invalid(form=form)
        )

    def form_valid(
        self, form: CustomerWialonUnitCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Retrieves a unit from Wialon and creates a :model:`terminusgps_tracker.CustomerWialonUnit` based on it.

        Also grants necessary permissions to the customer to view the unit in Wialon.

        """
        customer = Customer.objects.get(user=self.request.user)
        with WialonSession() as session:
            unit: WialonUnit = wialon_utils.get_unit_by_imei(
                imei=form.cleaned_data["imei"], session=session
            )
            resource = WialonResource(
                id=customer.wialon_resource_id, session=session
            )
            end_user = WialonUser(id=customer.wialon_user_id, session=session)

            end_user.grant_access(
                unit, access_mask=wialon_constants.ACCESSMASK_UNIT_BASIC
            )
            unit.rename(form.cleaned_data["name"])
            resource.migrate_unit(unit)
            CustomerWialonUnit.objects.create(
                id=unit.id,
                name=unit.name,
                imei=unit.imei_number,
                customer=customer,
            )
        return super().form_valid(form=form)


class CustomerTransactionListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Transaction List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/partials/_transaction_list.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/transaction_list.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds the transaction list to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["transaction_list"] = self.get_transaction_list()
        return context

    def get_transaction_list(self) -> list[dict[str, typing.Any]]:
        """Returns a list of transactions from the customer's subscription."""
        try:
            customer = Customer.objects.get(user=self.request.user)
            return customer.subscription.authorizenet_get_transactions()
        except Subscription.DoesNotExist:
            return [{}]
