from typing import Any

from authorizenet.apicontractsv1 import customerAddressType, paymentType
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
)
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
    CustomerSubscription,
)
from terminusgps_tracker.views.mixins import (
    HtmxTemplateResponseMixin,
    TrackerAppConfigContextMixin,
)

if not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class CustomerDashboardView(
    LoginRequiredMixin,
    TrackerAppConfigContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    permission_denied_message = "Please login and try again."
    raise_exception = False
    template_name = "terminusgps_tracker/dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["customer"], _ = Customer.objects.get_or_create(user=self.request.user)
        context["subscription"], _ = CustomerSubscription.objects.get_or_create(
            customer=context["customer"]
        )
        context["subtitle"] = mark_safe(
            f"Check out the Terminus GPS <a class='text-terminus-red-800 underline decoration-terminus-black decoration underline-offset-4 hover:text-terminus-red-500 hover:decoration-dotted dark:text-terminus-red-400 dark:hover:text-terminus-red-200 dark:decoration-white' href='{reverse('mobile apps')}'>mobile app</a>!"
        )
        return context


class CustomerPaymentsView(
    LoginRequiredMixin,
    TrackerAppConfigContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    extra_context = {
        "title": "Payments",
        "subtitle": "Update your payment information",
        "class": "flex flex-col gap-8",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_payments.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/payments.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["customer"], _ = Customer.objects.get_or_create(user=self.request.user)
        context["subscription"], _ = CustomerSubscription.objects.get_or_create(
            customer=context["customer"]
        )
        return context


class CustomerAccountView(
    LoginRequiredMixin,
    TrackerAppConfigContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    extra_context = {"title": "Your Account", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_account.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/account.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["customer"], _ = Customer.objects.get_or_create(user=self.request.user)
        context["subscription"], _ = CustomerSubscription.objects.get_or_create(
            customer=context["customer"]
        )
        if self.request.user.first_name:
            context["title"] = f"{self.request.user.first_name}'s Account"
        return context


class CustomerSupportView(
    LoginRequiredMixin,
    TrackerAppConfigContextMixin,
    HtmxTemplateResponseMixin,
    TemplateView,
):
    content_type = "text/html"
    extra_context = {
        "title": "Support",
        "subtitle": "Drop us a line",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_support.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/support.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        for email in settings.TRACKER_APP_CONFIG["EMAILS"]:
            if email["NAME"] == "SUPPORT":
                context["support_link"] = email["OPTIONS"]["link"]
        return context


class CustomerShippingAddressCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"class": "flex flex-col gap-4", "title": "Add Shipping Address"}
    form_class = CustomerShippingAddressCreateForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("payments")
    template_name = "terminusgps_tracker/addresses/create.html"

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        if self.request.user:
            initial["first_name"] = self.request.user.first_name
            initial["last_name"] = self.request.user.last_name
        return initial

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
            return super().form_valid(form=form)
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


class CustomerShippingAddressListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "address_list"
    extra_context = {"title": "Shipping Addresses", "class": "flex flex-col gap-4"}
    http_method_names = ["get", "patch"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer: Customer = Customer.objects.get(user=self.request.user)
        customer.authorizenet_sync_address_profiles()
        return super().get(request, *args, **kwargs)

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerShippingAddressDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get", "patch"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_detail.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/detail.html"

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get("default"):
            self.set_default_address(kwargs["pk"])
        return HttpResponseRedirect(reverse("list addresses"))

    @transaction.atomic
    def set_default_address(self, address_pk: int) -> None:
        target_addr = self.get_queryset().get(pk=address_pk)
        target_addr.default = True
        target_addr.save()

        other_addrs = self.get_queryset().exclude(pk=address_pk)
        for addr in other_addrs:
            addr.default = False
        CustomerShippingAddress.objects.bulk_update(other_addrs, ["default"])

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
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "address"
    http_method_names = ["post"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_delete.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("list addresses")
    template_name = "terminusgps_tracker/addresses/delete.html"

    def get_queryset(
        self,
    ) -> QuerySet[CustomerShippingAddress, CustomerShippingAddress]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerPaymentMethodCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"class": "flex flex-col gap-4", "title": "Add Payment Method"}
    form_class = CustomerPaymentMethodCreateForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_create.html"
    permission_denied_message = "Please login in order to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    success_url = reverse_lazy("payments")
    template_name = "terminusgps_tracker/payments/create.html"

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        if self.request.user:
            initial["first_name"] = self.request.user.first_name
            initial["last_name"] = self.request.user.last_name
        return initial

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

            if form.cleaned_data["create_shipping_address"]:
                address_profile = AddressProfile(
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


class CustomerPaymentMethodListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "payment_list"
    extra_context = {"title": "Payment Methods", "class": "flex flex-col gap-4"}
    http_method_names = ["get", "patch"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/payments/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer: Customer = Customer.objects.get(user=self.request.user)
        customer.authorizenet_sync_payment_profiles()
        return super().get(request, *args, **kwargs)

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerPaymentMethodDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get", "patch"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_detail.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/payments/detail.html"

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get("default"):
            self.set_default_payment(kwargs["pk"])
        return HttpResponseRedirect(reverse("list payments"))

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

    @transaction.atomic
    def set_default_payment(self, payment_pk: int) -> None:
        target_payment = self.get_queryset().get(pk=payment_pk)
        target_payment.default = True
        target_payment.save()

        other_payments = self.get_queryset().exclude(pk=payment_pk)
        for payment in other_payments:
            payment.default = False
        CustomerPaymentMethod.objects.bulk_update(other_payments, ["default"])


class CustomerPaymentMethodDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "payment"
    http_method_names = ["post"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_delete.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("list payments")
    template_name = "terminusgps_tracker/payments/delete.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        prompt: str | None = request.headers.get("HX-Prompt")

        if not prompt or not prompt.isdigit():
            return HttpResponse(status=400)
        if int(prompt) != self.get_object().authorizenet_get_payment_profile().last_4:
            return HttpResponse(status=400)
        return super().post(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomerPaymentMethod, CustomerPaymentMethod]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)
