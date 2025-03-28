from django.db.models import QuerySet
from django.views.generic import DetailView, FormView, ListView

from terminusgps_tracker.forms import CustomerAssetCreateForm
from terminusgps_tracker.models.customers import Customer, CustomerAsset
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class CustomerAssetDetailView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get", "patch"]
    model = CustomerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    queryset = CustomerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/detail.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)


class CustomerAssetCreateView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"class": "flex flex-col gap-4", "title": "Register Asset"}
    http_method_names = ["get", "post"]
    model = CustomerAsset
    form_class = CustomerAssetCreateForm
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    queryset = CustomerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/create.html"


class CustomerAssetListView(CustomerRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    model = CustomerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    queryset = CustomerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/list.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        queryset: QuerySet = super().get_queryset()
        customer: Customer = Customer.objects.get(user=self.request.user)
        return queryset.filter(customer=customer)
