import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, TemplateView
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.profiles import AddressProfile, PaymentProfile
from terminusgps.authorizenet.utils import (
    generate_customer_address,
    generate_customer_payment,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import (
    CustomerPaymentMethodCreationForm,
    CustomerShippingAddressCreationForm,
)
from terminusgps_tracker.models.customers import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
)


class CustomerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "Download the Terminus GPS mobile app today!",
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
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["transaction_list"] = self.get_subscription_transactions()
        return context

    def get_subscription_transactions(self) -> list[dict[str, typing.Any]]:
        return (
            self.get_customer().subscription.authorizenet_get_transactions()
            if self.get_customer()
            else []
        )

    def get_customer(self) -> Customer | None:
        try:
            return Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            return


class CustomerPaymentMethodListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    extra_context = {"title": "Payment Method List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    ordering = "id"
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=request.user)
        customer.authorizenet_sync_payment_profiles()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return CustomerPaymentMethod.objects.filter(
            customer__user=self.request.user
        ).order_by(self.get_ordering())


class CustomerPaymentMethodDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"title": "Payment Method Details"}
    http_method_names = ["get", "delete"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/detail.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        prompt = request.headers.get("HX-Prompt", "")
        last_4 = self.get_object().authorizenet_get_last_4()
        if prompt and prompt.isdigit() and int(prompt) == last_4:
            customer_payment = self.get_object()
            payment_profile = PaymentProfile(
                customer_profile_id=customer_payment.customer.authorizenet_profile_id,
                id=customer_payment.id,
            )
            payment_profile.delete()
            customer_payment.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=406)

    def get_queryset(self):
        return CustomerPaymentMethod.objects.filter(
            customer__user=self.request.user
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        pprofile = self.get_object().authorizenet_get_profile()
        context["paymentProfile"] = pprofile.paymentProfile
        return context


class CustomerShippingAddressListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    extra_context = {"title": "Shipping Address List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    ordering = "id"
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=request.user)
        customer.authorizenet_sync_address_profiles()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).order_by(self.get_ordering())


class CustomerShippingAddressDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"title": "Shipping Address Details"}
    http_method_names = ["get", "delete"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/detail.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        try:
            customer_address = self.get_object()
            address_profile = AddressProfile(
                customer_profile_id=customer_address.customer.authorizenet_profile_id,
                id=customer_address.pk,
                default=customer_address.default,
            )
            address_profile.delete()
            customer_address.delete()
        except AuthorizenetControllerExecutionError:
            return HttpResponse(status=406)
        return HttpResponse(status=200)

    def get_queryset(self):
        return CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        aprofile = self.get_object().authorizenet_get_profile()
        context["addressProfile"] = aprofile.address
        return context


class CustomerShippingAddressCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Shipping Address"}
    form_class = CustomerShippingAddressCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/create.html"
    success_url = reverse_lazy("tracker:account")

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerShippingAddressCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(user=self.request.user)
            address_profile = AddressProfile(
                customer_profile_id=customer.authorizenet_profile_id,
                default=form.cleaned_data["default"],
            )
            CustomerShippingAddress.objects.create(
                id=address_profile.create(generate_customer_address(form)),
                customer=customer,
            )
        except AuthorizenetControllerExecutionError as e:
            message = _("Whoops! '%(error)s'")
            if e.code == "E00039":
                message = _("Whoops! This address already exists.")
            form.add_error(
                None, ValidationError(message, code="invalid", params={"e": e})
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class CustomerPaymentMethodCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Payment Method"}
    form_class = CustomerPaymentMethodCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/payments/create.html"
    success_url = reverse_lazy("tracker:account")

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerPaymentMethodCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(user=self.request.user)
            address = generate_customer_address(form)
            payment = generate_customer_payment(form)
            payment_profile = PaymentProfile(
                customer_profile_id=customer.authorizenet_profile_id,
                default=form.cleaned_data["default"],
            )
            CustomerPaymentMethod.objects.create(
                id=payment_profile.create(address=address, payment=payment),
                customer=customer,
            )
            if form.cleaned_data["create_shipping_address"]:
                address_profile = AddressProfile(
                    customer_profile_id=customer.authorizenet_profile_id,
                    default=form.cleaned_data["default"],
                )
                CustomerShippingAddress.objects.create(
                    id=address_profile.create(address), customer=customer
                )
        except AuthorizenetControllerExecutionError as e:
            message = _("Whoops! '%(error)s'")
            if e.code == "E00039":
                message = _(
                    "Whoops! The payment method or shipping address already exists."
                )
            form.add_error(
                None, ValidationError(message, code="invalid", params={"e": e})
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)
