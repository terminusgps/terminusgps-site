from django.db.models import QuerySet
from django.views.generic import ListView

from terminusgps_tracker.models import Customer, CustomerAsset
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class CustomerAssetListView(CustomerRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    extra_context = {"title": "Asset List", "subtitle": "Your vehicles at a glance"}
    context_object_name = "asset_list"
    model = CustomerAsset
    paginate_by = 25
    ordering = "wialon_id"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/list.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)
