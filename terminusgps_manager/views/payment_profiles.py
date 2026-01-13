import typing

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerPaymentProfile, CustomerProfile

from ..forms import CustomerPaymentProfileCreateForm


class CustomerPaymentProfileCreateView(HtmxTemplateResponseMixin, CreateView):
    content_type = "text/html"
    form_class = CustomerPaymentProfileCreateForm
    http_method_names = ["get", "post"]
    model = CustomerPaymentProfile
    pk_url_kwarg = "paymentprofile_pk"
    template_name = "terminusgps_manager/payment_profiles/create.html"

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:list payment profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context

    def form_valid(
        self, form: CustomerPaymentProfileCreateForm
    ) -> HttpResponse:
        try:
            obj = form.save(commit=False)
            obj.cprofile = CustomerProfile.objects.get(
                pk=self.kwargs["customerprofile_pk"]
            )
            obj.save()
            obj.save(push=False)
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


class CustomerPaymentProfileDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    pk_url_kwarg = "paymentprofile_pk"
    template_name = "terminusgps_manager/payment_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerPaymentProfileUpdateView(HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    pk_url_kwarg = "paymentprofile_pk"
    template_name = "terminusgps_manager/payment_profiles/update.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerPaymentProfileDeleteView(DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = CustomerPaymentProfile
    pk_url_kwarg = "paymentprofile_pk"

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:list payment profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            response = super().form_valid(form=form)
            response.headers["HX-Retarget"] = "#payment-profiles"
            return response
        except AuthorizenetControllerExecutionError as error:
            return HttpResponse(
                bytes(str(error), encoding="utf-8"), status=406
            )

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerPaymentProfileListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    ordering = "pk"
    pk_url_kwarg = "paymentprofile_pk"
    template_name = "terminusgps_manager/payment_profiles/list.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        ).order_by(self.get_ordering())

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context
