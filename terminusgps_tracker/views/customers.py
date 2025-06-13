import typing

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants as wialon_constants
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["subscription"] = Subscription.objects.get(
                customer__user=self.request.user
            )
        except Subscription.DoesNotExist:
            context["subscription"] = None
        return context


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
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/detail.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        """Retrieves associated Wialon units for the customer."""
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer__user=self.request.user)


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
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        """Retrieves associated Wialon units for the customer."""
        if self.request.user.is_staff:
            return super().get_queryset().order_by(self.get_ordering())
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )


class CustomerWialonUnitListDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Unit Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = (
        "terminusgps_tracker/units/partials/_list_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list_detail.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer__user=self.request.user)


class CustomerWialonUnitListDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "unit"
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = (
        "terminusgps_tracker/units/partials/_list_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list_delete.html"
    success_url = reverse_lazy("tracker:unit list")

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer__user=self.request.user)


class CustomerWialonUnitListUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Update Unit"}
    fields = ["name", "tier"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = (
        "terminusgps_tracker/units/partials/_list_update.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list_update.html"

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        for name in form.fields:
            form.fields[name].widget.attrs.update(
                {"class": settings.DEFAULT_FIELD_CLASS}
            )
        return form

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer__user=self.request.user)

    def get_success_url(self) -> str:
        return reverse(
            "tracker:unit list detail",
            kwargs={"unit_pk": self.get_object().pk},
        )

    def form_valid(
        self, form: forms.Form
    ) -> HttpResponse | HttpResponseRedirect:
        with WialonSession() as session:
            new_name = form.cleaned_data["name"]
            unit = WialonUnit(self.get_object().pk, session)

            if new_name != unit.name:
                unit.rename(new_name)
            return super().form_valid(form=form)


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
        if not customer.payments.exists():
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Please add at least one payment method first."),
                    code="invalid",
                ),
            )
        if not customer.addresses.exists():
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Please add at least one shipping address first."
                    ),
                    code="invalid",
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
        with WialonSession() as session:
            customer = Customer.objects.get(user=self.request.user)
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
                tier=form.cleaned_data["tier"],
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
