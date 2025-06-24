import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.profiles import AddressProfile, PaymentProfile
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
from terminusgps_tracker.views.mixins import CustomerOrStaffRequiredMixin


class CustomerPaymentMethodListView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    ListView,
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "payment_list"
    extra_context = {"title": "Payment Method List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    ordering = "pk"
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        customer.authorizenet_sync_payment_profiles()
        return super().get(request, *args, **kwargs)

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )


class CustomerPaymentMethodDetailView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"title": "Payment Method Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/detail.html"
    pk_url_kwarg = "payment_pk"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["profile"] = self.get_object().authorizenet_get_profile()
            return context
        except (
            AuthorizenetControllerExecutionError,
            CustomerPaymentMethod.DoesNotExist,
        ):
            context["profile"] = None
            return context


class CustomerPaymentMethodDeleteView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DeleteView,
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"title": "Delete Payment Method"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    success_url = reverse_lazy("tracker:payment list")
    template_name = "terminusgps_tracker/payments/delete.html"
    pk_url_kwarg = "payment_pk"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        return CustomerPaymentMethod.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def form_valid(self, form=None) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
            payment_profile = PaymentProfile(
                id=self.object.pk,
                customer_profile_id=customer.authorizenet_profile_id,
            )
            payment_profile.delete()
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00105":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! This payment method is associated with an active or suspended subscription. Nothing was deleted."
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
                        ),
                    )
            return self.form_invalid(form=form)

    def form_invalid(self, form=None) -> HttpResponse:
        response = self.render_to_response(self.get_context_data(form=form))
        response.headers["HX-Retarget"] = f"#payment-{self.object.pk}"
        return response


class CustomerPaymentMethodCreateView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    FormView,
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
    success_url = reverse_lazy("tracker:account")
    template_name = "terminusgps_tracker/payments/create.html"

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        initial["first_name"] = customer.user.first_name
        initial["last_name"] = customer.user.last_name
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
                customer_profile_id=customer.authorizenet_profile_id
            )
            CustomerPaymentMethod.objects.create(
                id=payment_profile.create(payment=payment, address=address),
                customer=customer,
            )

            if form.cleaned_data["create_shipping_address"]:
                address_profile = AddressProfile(
                    customer_profile_id=customer.authorizenet_profile_id
                )
                CustomerShippingAddress.objects.create(
                    id=address_profile.create(address=address),
                    customer=customer,
                )
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00039":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! A duplicate payment method or shipping address already exists."
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
