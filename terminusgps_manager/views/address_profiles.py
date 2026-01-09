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
from terminusgps_payments.models import CustomerAddressProfile, CustomerProfile

from ..forms import CustomerAddressProfileCreateForm


class CustomerAddressProfileCreateView(HtmxTemplateResponseMixin, CreateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = CustomerAddressProfile
    template_name = "terminusgps_manager/address_profiles/create.html"
    form_class = CustomerAddressProfileCreateForm

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:list address profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context

    def form_valid(
        self, form: CustomerAddressProfileCreateForm
    ) -> HttpResponse:
        try:
            obj = form.save(commit=False)
            obj.cprofile = CustomerProfile.objects.get(
                pk=self.kwargs["customerprofile_pk"]
            )
            obj.save()
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as error:
            match error.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            "%(error)s",
                            code="invalid",
                            params={"error": error},
                        ),
                    )
            return self.form_invalid(form=form)


class CustomerAddressProfileDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    template_name = "terminusgps_manager/address_profiles/detail.html"
    pk_url_kwarg = "addressprofile_pk"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerAddressProfileUpdateView(HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get"]
    fields = ["first_name", "last_name", "address"]
    model = CustomerAddressProfile
    template_name = "terminusgps_manager/address_profiles/update.html"
    pk_url_kwarg = "addressprofile_pk"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerAddressProfileDeleteView(DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = CustomerAddressProfile
    pk_url_kwarg = "addressprofile_pk"

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_manager:list address profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            response = super().form_valid(form=form)
            response.headers["HX-Retarget"] = "#address-profiles"
            return response
        except AuthorizenetControllerExecutionError as error:
            return HttpResponse(
                bytes(str(error), encoding="utf-8"), status=406
            )

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerAddressProfileListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    ordering = "pk"
    template_name = "terminusgps_manager/address_profiles/list.html"

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
