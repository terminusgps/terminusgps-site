from django.views.generic import DetailView, ListView
from terminusgps.mixins import HtmxTemplateResponseMixin

from .. import models


class WialonUnitListView(HtmxTemplateResponseMixin, ListView):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.WialonUnit
    ordering = "name"
    paginate_by = 8
    template_name = "terminusgps_manager/units/list.html"


class WialonUnitDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.WialonUnit
    template_name = "terminusgps_manager/units/detail.html"
