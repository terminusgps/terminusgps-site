from django.views.generic import TemplateView

from terminusgps_tracker.models.service import AuthService


class DashboardView(TemplateView):
    content_type = "text/html"
    extra_context = {"services": AuthService.objects.all()}
    template_name = "terminusgps_tracker/dashboard.html"
    http_method_names = ["get", "post"]
