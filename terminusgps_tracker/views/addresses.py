import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import profiles
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.utils import generate_customer_address
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

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerShippingAddressCreationForm
    ) -> HttpResponse:
        try:
            customer = Customer.objects.get(user=self.request.user)
            response = profiles.create_customer_shipping_address(
                customer_profile_id=customer.authorizenet_profile_id,
                new_address=generate_customer_address(form),
                default=form.cleaned_data["default"],
            )
            CustomerShippingAddress.objects.create(
                id=int(response.customerAddressId), customer=customer
            )
            return HttpResponseRedirect(
                reverse(
                    "tracker:list address", kwargs={"customer_pk": customer.pk}
                )
            )
        except AuthorizenetControllerExecutionError as e:
            match e.code:
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
        address: CustomerShippingAddress = kwargs["object"]
        context["profile"] = profiles.get_customer_shipping_address(
            customer_profile_id=address.customer.authorizenet_profile_id,
            customer_address_profile_id=address.pk,
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
        ).select_related("customer")

    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            profiles.delete_customer_shipping_address(
                customer_profile_id=Customer.objects.get(
                    pk=self.kwargs["customer_pk"]
                ).authorizenet_profile_id,
                customer_address_profile_id=self.object.pk,
            )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
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
        address: CustomerShippingAddress = kwargs["object"]
        context["profile"] = profiles.get_customer_shipping_address(
            customer_profile_id=address.customer.authorizenet_profile_id,
            customer_address_profile_id=address.pk,
        )
        return context


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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        self.sync_customer_address_profiles(customer)
        return super().get(request, *args, **kwargs)

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

    @transaction.atomic
    def sync_customer_address_profiles(self, customer: Customer) -> None:
        """Syncs the customer's shipping addresses with Authorizenet."""
        remote_ids = self.get_remote_address_profile_ids(customer)
        local_ids = self.get_local_address_profile_ids(customer)
        ids_to_create = set(remote_ids) - set(local_ids) if remote_ids else []
        ids_to_delete = set(local_ids) - set(remote_ids) if local_ids else []

        if ids_to_create:
            CustomerShippingAddress.objects.bulk_create(
                [
                    CustomerShippingAddress(id=id, customer=customer)
                    for id in ids_to_create
                ],
                ignore_conflicts=True,
            )

        if ids_to_delete:
            CustomerShippingAddress.objects.filter(
                id__in=ids_to_delete, customer=customer
            ).delete()

    @staticmethod
    def get_local_address_profile_ids(customer: Customer) -> list[int]:
        """Returns a list of address profile ids for the customer from the local database."""
        return list(customer.addresses.values_list("id", flat=True))

    @staticmethod
    def get_remote_address_profile_ids(customer: Customer) -> list[int]:
        """Returns a list of address profile ids for the customer from Authorizenet."""
        if cached_response := cache.get(f"get_customer_profile_{customer.pk}"):
            response = cached_response
        else:
            response = profiles.get_customer_profile(
                customer_profile_id=customer.authorizenet_profile_id,
                include_issuer_info=False,
            )
            cache.set(
                f"get_customer_profile_{customer.pk}", response, timeout=60 * 3
            )

        if response is None or not all(
            [
                hasattr(response, "profile"),
                hasattr(response.profile, "shipToList"),
            ]
        ):
            return []
        return [
            int(address.customerAddressId)
            for address in response.profile.shipToList
        ]
