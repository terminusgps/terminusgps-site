import typing

from authorizenet import apicontractsv1
from django import forms
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import profiles
from terminusgps.authorizenet.utils import (
    generate_customer_address,
    generate_customer_payment,
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
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Payment Method"}
    form_class = CustomerPaymentMethodCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_create.html"
    )
    success_url = reverse_lazy("tracker:list payment")
    template_name = "terminusgps_tracker/payments/create.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    def form_valid(
        self, form: CustomerPaymentMethodCreationForm
    ) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        response = profiles.create_customer_payment_profile(
            customer_profile_id=customer.authorizenet_profile_id,
            new_payment_profile=apicontractsv1.customerPaymentProfileType(
                payment=generate_customer_payment(form),
                billTo=generate_customer_address(form),
            ),
        )
        CustomerPaymentMethod.objects.create(
            id=int(response.customerPaymentProfileId), customer=customer
        )
        if form.cleaned_data["create_shipping_address"]:
            response = profiles.create_customer_shipping_address(
                customer_profile_id=customer.authorizenet_profile_id,
                new_address=generate_customer_address(form),
            )
            CustomerShippingAddress.objects.create(
                id=int(response.customerAddressId), customer=customer
            )
        return super().form_valid(form=form)


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
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = profiles.get_customer_payment_profile(
            customer_profile_id=Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id,
            customer_payment_profile_id=kwargs["object"].pk,
        )
        return context


class CustomerPaymentMethodDeleteView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "payment"
    http_method_names = ["get", "post"]
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_delete.html"
    )
    pk_url_kwarg = "payment_pk"
    queryset = CustomerPaymentMethod.objects.none()
    template_name = "terminusgps_tracker/payments/delete.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def form_valid(self, form: forms.Form) -> HttpResponse:
        profiles.delete_customer_payment_profile(
            customer_profile_id=Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id,
            customer_payment_profile_id=self.object.pk,
        )
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = profiles.get_customer_payment_profile(
            customer_profile_id=Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id,
            customer_payment_profile_id=kwargs["object"].pk,
        )
        return context


class CustomerPaymentMethodListView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"title": "Customer Payment Method List"}
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
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).order_by(self.get_ordering())
