import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    Subscription,
)


class SubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "sub_pk"
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/detail.html"
    queryset = Subscription.objects.select_related(
        "customer", "payment", "address"
    )

    def get_object(self) -> Subscription:
        if self.request.user and self.request.user.is_staff:
            return super().get_object()
        return self.get_queryset().get(customer__user=self.request.user)


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    extra_context = {"title": "Update Subscription"}
    http_method_names = ["get", "post"]
    fields = ["payment", "address", "features"]
    login_url = reverse_lazy("login")
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_update.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "sub_pk"
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/update.html"

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()

    def get_initial(self) -> dict[str, typing.Any]:
        try:
            initial: dict[str, typing.Any] = super().get_initial()
            initial["customer"] = Customer.objects.get(user=self.request.user)
            return initial
        except Customer.DoesNotExist:
            return initial

    def get_object(self) -> Subscription:
        if self.request.user and self.request.user.is_staff:
            return super().get_object()
        return self.get_queryset().get(customer__user=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form = self.authorizenet_generate_payment_choices(form)
        form = self.authorizenet_generate_address_choices(form)
        for name in form.fields:
            form.fields[name].widget.attrs.update(
                {"class": settings.DEFAULT_FIELD_CLASS}
            )
        form.fields["features"].label = "Additional Features"
        form.fields[
            "features"
        ].help_text = 'Hold down "Control", or "Command" on a Mac, to select more than one.'
        return form

    def authorizenet_generate_payment_choices(self, form: Form) -> Form:
        qs = CustomerPaymentMethod.objects.filter(
            customer__user=self.request.user
        )
        form.fields["payment"].choices = (
            (payment.pk, f"Card ending in {payment.authorizenet_get_last_4()}")
            for payment in qs
        )
        return form

    def authorizenet_generate_address_choices(self, form: Form) -> Form:
        qs = CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        )
        form.fields["address"].choices = (
            (
                address.pk,
                f"{address.authorizenet_get_profile().address.address}",
            )
            for address in qs
        )
        return form


class SubscriptionDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    extra_context = {"title": "Cancel Subscription"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "sub_pk"
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/delete.html"

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()

    def get_object(self) -> Subscription:
        if self.request.user and self.request.user.is_staff:
            return super().get_object()
        return self.get_queryset().get(customer__user=self.request.user)


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    extra_context = {"title": "Create Subscription"}
    http_method_names = ["get", "post"]
    fields = ["payment", "address", "features"]
    login_url = reverse_lazy("login")
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/create.html"

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()
