import typing

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerProfile, Subscription

from ..forms import SubscriptionCreateForm
from ..models import TerminusGPSCustomer


class SubscriptionCreateView(HtmxTemplateResponseMixin, CreateView):
    content_type = "text/html"
    form_class = SubscriptionCreateForm
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )
        self.cprofile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = self.cprofile
        return context

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        form.fields["pprofile"].queryset = self.cprofile.payment_profiles.all()
        form.fields["aprofile"].queryset = self.cprofile.address_profiles.all()
        return form

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            sub = form.save(commit=False)
            sub.name = "Terminus GPS Subscription"
            sub.amount = self.customer.grand_total
            sub.cprofile = self.cprofile
            sub.save()
            self.customer.subscription = sub
            self.customer.save(update_fields=["subscription"])
            return HttpResponseRedirect(
                reverse(
                    "terminusgps_manager:detail subscriptions",
                    kwargs={"subscription_pk": sub.pk},
                )
            )
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    _("%(error)s"),
                    code="invalid",
                    params={"error": str(error)},
                ),
            )
            return self.form_invalid(form=form)


class SubscriptionDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/detail.html"


class SubscriptionUpdateView(HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    fields = ["aprofile", "pprofile"]
    http_method_names = ["get", "post"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/update.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.cprofile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        form.fields["pprofile"].queryset = self.cprofile.payment_profiles.all()
        form.fields["pprofile"].empty_label = None
        form.fields["aprofile"].queryset = self.cprofile.address_profiles.all()
        form.fields["aprofile"].empty_label = None
        return form

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:detail subscriptions",
            kwargs={"subscription_pk": self.object.pk},
        )


class SubscriptionDeleteView(HtmxTemplateResponseMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    success_url = reverse_lazy("terminusgps_manager:create subscriptions")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            return HttpResponse(str(error).encode("utf-8"), status=406)
