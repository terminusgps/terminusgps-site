import datetime
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
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
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        context["greeting"] = self.get_greeting(now)
        return context

    def get_greeting(self, dt: datetime.datetime) -> str:
        return "Good morning" if dt.hour <= 12 else "Good afternoon"


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_account.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/account.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=self.request.user)
        if customer.payments.count == 0:
            customer.authorizenet_sync_payment_profiles()
        if customer.addresses.count == 0:
            customer.authorizenet_sync_address_profiles()
        return super().get(request, *args, **kwargs)


class CustomerPaymentMethodListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    extra_context = {"title": "Payment Method List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/list.html"
    ordering = "id"

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
        pprofile = self.get_object().authorizenet_get_payment_profile()
        last_4 = int(
            str(pprofile.paymentProfile.payment.creditCard.cardNumber)[4:]
        )
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
        pprofile = self.get_object().authorizenet_get_payment_profile()
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
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/list.html"
    ordering = "id"

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
        customer_address = self.get_object()
        address_profile = AddressProfile(
            customer_profile_id=customer_address.customer.authorizenet_profile_id,
            id=customer_address.pk,
        )
        address_profile.delete()
        customer_address.delete()
        return HttpResponse(status=200)

    def get_queryset(self):
        return CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        aprofile = self.get_object().authorizenet_get_address_profile()
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
            payment_profile = PaymentProfile(
                customer_profile_id=customer.authorizenet_profile_id,
                default=form.cleaned_data["default"],
            )
            CustomerPaymentMethod.objects.create(
                id=payment_profile.create(
                    address=generate_customer_address(form),
                    payment=generate_customer_payment(form),
                ),
                customer=customer,
            )
        except AuthorizenetControllerExecutionError as e:
            message = _("Whoops! '%(error)s'")
            if e.code == "E00039":
                message = _("Whoops! This payment method already exists.")
            form.add_error(
                None, ValidationError(message, code="invalid", params={"e": e})
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)
