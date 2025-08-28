import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import profiles
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import CustomerShippingAddressCreationForm
from terminusgps_tracker.models import Customer, CustomerShippingAddress
from terminusgps_tracker.views.mixins import (
    CustomerAuthenticationRequiredMixin,
)


class CustomerShippingAddressCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Add Shipping Address"}
    form_class = CustomerShippingAddressCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("tracker:account")
    template_name = "terminusgps_tracker/addresses/create.html"

    @transaction.atomic
    def form_valid(
        self, form: CustomerShippingAddressCreationForm
    ) -> HttpResponse:
        try:
            customer = Customer.objects.get(user=self.request.user)
            shipping_address = CustomerShippingAddress(customer=customer)
            response = profiles.create_customer_shipping_address(
                customer_profile_id=customer.authorizenet_profile_id,
                new_address=form.cleaned_data["address"],
                default=form.cleaned_data["default"],
            )
            shipping_address.pk = int(response.customerAddressId)
            shipping_address.save()
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
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = (
            kwargs["object"].get_authorizenet_profile()
            if kwargs.get("object") is not None
            else None
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

    def get_success_url(self) -> str:
        address = self.get_object()
        return address.get_list_url()

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        return CustomerShippingAddress.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            address = self.get_object()
            profiles.delete_customer_shipping_address(
                customer_profile_id=address.customer.authorizenet_profile_id,
                customer_address_profile_id=address.pk,
            )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00107":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! The shipping address couldn't be deleted because it's associated with an active or suspended subscription."
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


class CustomerShippingAddressListView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "address_list"
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
        return (
            CustomerShippingAddress.objects.filter(
                customer__pk=self.kwargs["customer_pk"]
            )
            .select_related("customer")
            .order_by(self.get_ordering())
        )
