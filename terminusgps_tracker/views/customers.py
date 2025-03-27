from typing import Any

from authorizenet.apicontractsv1 import customerAddressType, paymentType
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet.errors import ControllerExecutionError
from terminusgps.authorizenet.profiles import AddressProfile, PaymentProfile
from terminusgps.authorizenet.utils import (
    generate_customer_address,
    generate_customer_payment,
)

from terminusgps_tracker.forms import (
    CustomerPaymentMethodCreateForm,
    CustomerShippingAddressCreateForm,
)
from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
)
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class CustomerShippingAddressCreateView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"class": "flex flex-col gap-4", "title": "Add Shipping Address"}
    form_class = CustomerShippingAddressCreateForm
    http_method_names = ["get", "post", "delete"]
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    queryset = Customer.objects.none()
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/addresses/create.html"

    def form_valid(
        self, form: CustomerShippingAddressCreateForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer: Customer = Customer.objects.get(user=self.request.user)
            address_obj: customerAddressType = generate_customer_address(form)
            address_profile: AddressProfile = AddressProfile(
                merchant_id=customer.user.pk,
                customer_profile_id=customer.authorizenet_id,
                default=form.cleaned_data["default"],
                id=None,
                address=address_obj,
            )

            CustomerShippingAddress.objects.create(
                customer=customer,
                default=form.cleaned_data["default"],
                authorizenet_id=int(address_profile.id),
            )
        except ControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        except Customer.DoesNotExist as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class CustomerShippingAddressListView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "address_list"
    extra_context = {"title": "Shipping Addresses", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    template_name = "terminusgps_tracker/addresses/list.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerShippingAddressDetailView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get", "patch"]
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_detail.html"
    template_name = "terminusgps_tracker/addresses/detail.html"

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        print(f"{request.GET = }")
        return super().patch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = (
            self.get_object().authorizenet_get_address_profile().get_details().address
        )
        return context

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerShippingAddressDeleteView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "address"
    http_method_names = ["post"]
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_delete.html"
    success_url = reverse_lazy("list addresses")
    template_name = "terminusgps_tracker/addresses/delete.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerPaymentMethodCreateView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"class": "flex flex-col gap-4", "title": "Add Payment Method"}
    form_class = CustomerPaymentMethodCreateForm
    http_method_names = ["get", "post"]
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_create.html"
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/payments/create.html"
    queryset = CustomerPaymentMethod.objects.none()

    def form_valid(
        self, form: CustomerPaymentMethodCreateForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer: Customer = Customer.objects.get(user=self.request.user)
            address_obj: customerAddressType = generate_customer_address(form)
            payment_obj: paymentType = generate_customer_payment(form)
            payment_profile = PaymentProfile(
                merchant_id=customer.user.pk,
                customer_profile_id=customer.authorizenet_id,
                default=form.cleaned_data["default"],
                id=None,
                address=address_obj,
                payment=payment_obj,
            )

            CustomerPaymentMethod.objects.create(
                customer=customer,
                default=form.cleaned_data["default"],
                authorizenet_id=int(payment_profile.id),
            )
        except ControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        except Customer.DoesNotExist as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class CustomerPaymentMethodListView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "payment_list"
    extra_context = {"title": "Payment Methods", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    template_name = "terminusgps_tracker/payments/list.html"

    def get_queryset(self) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerPaymentMethodDetailView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_detail.html"
    template_name = "terminusgps_tracker/payments/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = (
            self.get_object()
            .authorizenet_get_payment_profile()
            .get_details()
            .paymentProfile
        )
        return context

    def get_queryset(self) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerPaymentMethodDeleteView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "payment"
    http_method_names = ["post"]
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_delete.html"
    success_url = reverse_lazy("list payments")
    template_name = "terminusgps_tracker/payments/delete.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        prompt: str | None = request.headers.get("HX-Prompt")
        last_4: int = self.get_object().authorizenet_get_payment_profile().last_4

        if not prompt or not prompt.isdigit():
            return HttpResponse(status=401)
        if int(prompt) != last_4:
            return HttpResponse(status=401)
        return super().post(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)
