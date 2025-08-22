import typing

from authorizenet import apicontractsv1
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

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerPaymentMethodCreationForm
    ) -> HttpResponse:
        try:
            customer = Customer.objects.get(user=self.request.user)
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
            return HttpResponseRedirect(
                reverse(
                    "tracker:list payment", kwargs={"customer_pk": customer.pk}
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
        payment: CustomerPaymentMethod = kwargs["object"]
        context["profile"] = profiles.get_customer_payment_profile(
            customer_profile_id=payment.customer.authorizenet_profile_id,
            customer_payment_profile_id=payment.pk,
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
            profiles.delete_customer_payment_profile(
                customer_profile_id=Customer.objects.get(
                    pk=self.kwargs["customer_pk"]
                ).authorizenet_profile_id,
                customer_payment_profile_id=self.object.pk,
            )
            response = super().form_valid(form=form)
            response.headers["HX-Retarget"] = "#payment-list"
            return response
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
        context["profile"] = profiles.get_customer_payment_profile(
            customer_profile_id=payment.customer.authorizenet_profile_id,
            customer_payment_profile_id=payment.pk,
        )
        return context


class CustomerPaymentMethodListView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "payment_list"
    extra_context = {"title": "Customer Payment Method List"}
    http_method_names = ["get"]
    model = CustomerPaymentMethod
    ordering = "pk"
    paginate_by = 4
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    queryset = CustomerPaymentMethod.objects.none()
    template_name = "terminusgps_tracker/payments/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        self.sync_customer_payment_methods(customer)
        return super().get(request, *args, **kwargs)

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

    @transaction.atomic
    def sync_customer_payment_methods(self, customer: Customer) -> None:
        local_ids = self.get_local_payment_profile_ids(customer)
        remote_ids = self.get_remote_payment_profile_ids(customer)
        ids_to_create = set(remote_ids) - set(local_ids) if remote_ids else []
        ids_to_delete = set(local_ids) - set(remote_ids) if local_ids else []

        if ids_to_create:
            CustomerPaymentMethod.objects.bulk_create(
                [
                    CustomerPaymentMethod(id=id, customer=customer)
                    for id in ids_to_create
                ],
                ignore_conflicts=True,
            )

        if ids_to_delete:
            CustomerPaymentMethod.objects.filter(
                id__in=ids_to_delete, customer=customer
            ).delete()

    @staticmethod
    def get_local_payment_profile_ids(customer: Customer) -> list[int]:
        """Returns a list of payment profile ids for the customer from the local database."""
        return list(customer.payments.values_list("id", flat=True))

    @staticmethod
    def get_remote_payment_profile_ids(customer: Customer) -> list[int]:
        """Returns a list of the payment profile ids for the customer from Authorizenet."""
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
                hasattr(response.profile, "paymentProfiles"),
            ]
        ):
            return []
        return [
            int(paymentProfile.customerPaymentProfileId)
            for paymentProfile in response.profile.paymentProfiles
        ]
