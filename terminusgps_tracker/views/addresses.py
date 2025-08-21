import typing

from django import forms
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import profiles
from terminusgps.authorizenet.utils import generate_customer_address
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import CustomerShippingAddressCreationForm
from terminusgps_tracker.models import Customer, CustomerShippingAddress
from terminusgps_tracker.views.mixins import (
    CustomerAuthenticationRequiredMixin,
)


class CustomerShippingAddressCreateView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Shipping Address"}
    form_class = CustomerShippingAddressCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_create.html"
    )
    success_url = reverse_lazy("tracker:address list")
    template_name = "terminusgps_tracker/addresses/create.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    def form_valid(
        self, form: CustomerShippingAddressCreationForm
    ) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        response = profiles.create_customer_shipping_address(
            customer_profile_id=customer.authorizenet_profile_id,
            new_address=generate_customer_address(form),
            default=form.cleaned_data["default"],
        )
        CustomerShippingAddress.objects.create(
            id=int(response.customerAddressId), customer=customer
        )
        return super().form_valid(form=form)


class CustomerShippingAddressDetailView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "address"
    http_method_names = ["get"]
    model = CustomerShippingAddress
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_detail.html"
    )
    pk_url_kwarg = "address_pk"
    queryset = CustomerShippingAddress.objects.none()
    template_name = "terminusgps_tracker/addresses/detail.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        return CustomerShippingAddress.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = profiles.get_customer_shipping_address(
            customer_profile_id=Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id,
            customer_address_profile_id=kwargs["object"].pk,
        )
        return context


class CustomerShippingAddressDeleteView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "address"
    http_method_names = ["get", "post"]
    model = CustomerShippingAddress
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_delete.html"
    )
    pk_url_kwarg = "address_pk"
    queryset = CustomerShippingAddress.objects.none()
    template_name = "terminusgps_tracker/addresses/delete.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        return CustomerShippingAddress.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def form_valid(self, form: forms.Form) -> HttpResponse:
        profiles.delete_customer_shipping_address(
            customer_profile_id=Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id,
            customer_address_profile_id=self.object.pk,
        )
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = profiles.get_customer_shipping_address(
            customer_profile_id=Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id,
            customer_address_profile_id=kwargs["object"].pk,
        )
        return context


class CustomerShippingAddressListView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"title": "Customer Shipping Address List"}
    http_method_names = ["get"]
    model = CustomerShippingAddress
    ordering = "pk"
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    queryset = CustomerShippingAddress.objects.none()
    template_name = "terminusgps_tracker/addresses/list.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        return CustomerShippingAddress.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).order_by(self.get_ordering())
