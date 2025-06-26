import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.profiles import AddressProfile
from terminusgps.authorizenet.utils import generate_customer_address
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import CustomerShippingAddressCreationForm
from terminusgps_tracker.models.customers import (
    Customer,
    CustomerShippingAddress,
)
from terminusgps_tracker.views.mixins import CustomerOrStaffRequiredMixin


class CustomerShippingAddressListView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    ListView,
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "address_list"
    extra_context = {"title": "Shipping Address List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    ordering = "pk"
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        customer.authorizenet_sync_address_profiles()
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
    pk_url_kwarg = "address_pk"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        return CustomerShippingAddress.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["profile"] = self.get_object().authorizenet_get_profile()
        except (
            CustomerShippingAddress.DoesNotExist,
            AuthorizenetControllerExecutionError,
        ):
            context["profile"] = None
        return context


class CustomerShippingAddressDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"title": "Delete Shipping Address"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/delete.html"
    pk_url_kwarg = "address_pk"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        return CustomerShippingAddress.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def get_success_url(self) -> str:
        return reverse(
            "tracker:address list",
            kwargs={"customer_pk": self.kwargs["customer_pk"]},
        )

    def form_valid(self, form=None) -> HttpResponse | HttpResponseRedirect:
        try:
            aprofile_id = self.object.pk
            cprofile_id = Customer.objects.get(
                pk=self.kwargs["customer_pk"]
            ).authorizenet_profile_id

            aprofile = AddressProfile(
                id=aprofile_id, customer_profile_id=cprofile_id
            )
            aprofile.delete()
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00107":
                    # Address associated with subscription
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! This shipping address is associated with an active or suspended subscription. Nothing was deleted."
                            ),
                            code="invalid",
                        ),
                    )
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Something went wrong, nothing was deleted."
                            ),
                            code="invalid",
                            params={"e": e},
                        ),
                    )
            return self.form_invalid(form=form)

    def form_invalid(self, form=None) -> HttpResponse:
        response = self.render_to_response(self.get_context_data(form=form))
        response.headers["HX-Retarget"] = f"#address-{self.object.pk}"
        return response

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["addressProfile"] = (
                self.get_object()
                .authorizenet_get_profile()
                .find(f"{ANET_XMLNS}address")
            )
            return context
        except AuthorizenetControllerExecutionError:
            context["addressProfile"] = None
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
    success_url = reverse_lazy("tracker:account")
    template_name = "terminusgps_tracker/addresses/create.html"

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        initial["first_name"] = customer.user.first_name
        initial["last_name"] = customer.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerShippingAddressCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
            address = generate_customer_address(form)
            address_profile = AddressProfile(
                customer_profile_id=customer.authorizenet_profile_id,
                default=form.cleaned_data["default"],
            )
            CustomerShippingAddress.objects.create(
                id=address_profile.create(address), customer=customer
            )
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00039":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! A duplicate shipping address already exists."
                            ),
                            code="invalid",
                        ),
                    )
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Something went wrong. Please try again later."
                            ),
                            code="invalid",
                        ),
                    )
            return self.form_invalid(form=form)
