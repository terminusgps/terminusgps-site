import typing

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import utils
from terminusgps.wialon.session import WialonAPIError, WialonSession

from terminusgps_tracker.models import (
    Customer,
    CustomerWialonUnit,
    SubscriptionTier,
)


class CustomerWialonUnitCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    extra_context = {"title": "Register New Unit"}
    fields = ["name", "imei", "tier"]
    http_method_names = ["get", "post"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_create.html"
    success_url = reverse_lazy("terminusgps_tracker:list unit")
    template_name = "terminusgps_tracker/units/create.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["tier"] = SubscriptionTier.objects.first()
        if imei := str(self.request.GET.get("imei")):
            if imei.isdigit() and len(imei) <= 16:
                initial["imei"] = imei
        if self.request.user.first_name:
            initial["name"] = f"{self.request.user.first_name}'s Ride"
        return initial

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                customer = Customer.objects.get(user=self.request.user)
                imei = form.cleaned_data["imei"]
                name = form.cleaned_data["name"]
                tier = form.cleaned_data["tier"]
                wialon_unit = utils.get_unit_by_imei(imei, session)
                if wialon_unit is None:
                    raise WialonAPIError(
                        f"Couldn't find a Wialon unit with IMEI #: '{form.cleaned_data['imei']}'."
                    )
                if name != wialon_unit.get_name():
                    wialon_unit.set_name(name)
                customer_unit = CustomerWialonUnit()
                customer_unit.wialon_id = wialon_unit.id
                customer_unit.name = name
                customer_unit.imei = imei
                customer_unit.tier = tier
                customer_unit.customer = customer
                customer_unit.save()
                return HttpResponseRedirect(self.success_url)
        except WialonAPIError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end, please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)


class CustomerWialonUnitDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_detail.html"
    pk_url_kwarg = "unit_pk"
    template_name = "terminusgps_tracker/units/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self.get_object().name} Details"
        return context

    def get_queryset(self) -> QuerySet:
        return CustomerWialonUnit.objects.for_user(self.request.user)


class CustomerWialonUnitUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    fields = ["name", "tier"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_update.html"
    pk_url_kwarg = "unit_pk"
    template_name = "terminusgps_tracker/units/update.html"
    success_url = reverse_lazy("terminusgps_tracker:list unit")

    def get_queryset(self) -> QuerySet:
        return CustomerWialonUnit.objects.for_user(self.request.user)


class CustomerWialonUnitDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_delete.html"
    pk_url_kwarg = "unit_pk"
    template_name = "terminusgps_tracker/units/delete.html"

    def get_queryset(self) -> QuerySet:
        return CustomerWialonUnit.objects.for_user(self.request.user)


class CustomerWialonUnitListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "unit_list"
    http_method_names = ["get"]
    model = CustomerWialonUnit
    ordering = "name"
    paginate_by = 10
    partial_template_name = "terminusgps_tracker/units/partials/_list.html"
    template_name = "terminusgps_tracker/units/list.html"

    def get_queryset(self) -> QuerySet:
        return CustomerWialonUnit.objects.for_user(self.request.user).order_by(
            self.get_ordering()
        )
