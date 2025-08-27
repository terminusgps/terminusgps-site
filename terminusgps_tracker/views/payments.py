import typing

from authorizenet import apicontractsv1
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import profiles
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import CustomerPaymentMethodCreationForm
from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
)
from terminusgps_tracker.views.mixins import (
    CustomerAuthenticationRequiredMixin,
)


class CustomerPaymentMethodCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Add Payment Method"}
    form_class = CustomerPaymentMethodCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("tracker:account")
    template_name = "terminusgps_tracker/payments/create.html"

    @transaction.atomic
    def form_valid(
        self, form: CustomerPaymentMethodCreationForm
    ) -> HttpResponse:
        try:
            customer = Customer.objects.get(user=self.request.user)
            response = profiles.create_customer_payment_profile(
                customer_profile_id=customer.authorizenet_profile_id,
                new_payment_profile=apicontractsv1.customerPaymentProfileType(
                    billTo=form.cleaned_data["address"],
                    payment=apicontractsv1.paymentType(
                        creditCard=form.cleaned_data["credit_card"]
                    ),
                    defaultPaymentProfile=form.cleaned_data["default"],
                ),
            )
            CustomerPaymentMethod.objects.create(
                id=int(response.customerPaymentProfileId), customer=customer
            )
            if form.cleaned_data["create_shipping_address"]:
                response = profiles.create_customer_shipping_address(
                    customer_profile_id=customer.authorizenet_profile_id,
                    new_address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                )
                CustomerShippingAddress.objects.create(
                    id=int(response.customerAddressId), customer=customer
                )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("%(code)s: '%(message)s'"),
                            code="invalid",
                            params={"code": e.code, "message": e.message},
                        ),
                    )
            return self.form_invalid(form=form)


class CustomerPaymentMethodDetailView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "payment"
    http_method_names = ["get"]
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_detail.html"
    )
    pk_url_kwarg = "payment_pk"
    queryset = CustomerPaymentMethod.objects.none()
    template_name = "terminusgps_tracker/payments/detail.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if kwargs.get("object"):
            context["profile"] = kwargs["object"].get_authorizenet_profile()
        return context


class CustomerPaymentMethodDeleteView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"title": "Payment Method Delete"}
    http_method_names = ["get", "post"]
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_delete.html"
    )
    pk_url_kwarg = "payment_pk"
    queryset = CustomerPaymentMethod.objects.none()
    template_name = "terminusgps_tracker/payments/delete.html"

    def get_success_url(self) -> str:
        return reverse(
            "tracker:list payment",
            kwargs={"customer_pk": self.kwargs["customer_pk"]},
        )

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    @transaction.atomic
    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            customer_pk: int = self.kwargs["customer_pk"]
            customer: Customer = Customer.objects.get(pk=customer_pk)
            payment: CustomerPaymentMethod = self.get_object()

            profiles.delete_customer_payment_profile(
                customer_profile_id=customer.authorizenet_profile_id,
                customer_payment_profile_id=payment.pk,
            )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00105":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! The payment method couldn't be deleted because it's associated with an active or suspended subscription."
                            )
                        ),
                    )
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Something went wrong, please try again later."
                            )
                        ),
                    )
            return self.form_invalid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if kwargs.get("object"):
            context["profile"] = kwargs["object"].get_authorizenet_profile()
        return context


class CustomerPaymentMethodListView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "payment_list"
    extra_context = {"title": "Payment Method List"}
    http_method_names = ["get"]
    model = CustomerPaymentMethod
    ordering = "pk"
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    queryset = CustomerPaymentMethod.objects.none()
    template_name = "terminusgps_tracker/payments/list.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return (
            CustomerPaymentMethod.objects.filter(
                customer__pk=self.kwargs["customer_pk"]
            )
            .select_related("customer")
            .order_by(self.get_ordering())
        )
