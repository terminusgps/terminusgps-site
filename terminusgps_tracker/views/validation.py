from terminusgps_tracker.views.base import HtmxTemplateView


class ValidationView(HtmxTemplateView):
    template_name = "terminusgps_tracker/validate.html"
    partial_template_name = "terminusgps_tracker/partials/_validate.html"
