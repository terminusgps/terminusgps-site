from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.models import CustomerWialonUnit


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


class CustomerWialonUnitDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_detail.html"
    pk_url_kwarg = "unit_pk"
    template_name = "terminusgps_tracker/units/detail.html"

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
