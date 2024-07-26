from django.views.generic import TemplateView

from terminusgps_tracker.models.service import AuthService


class DashboardView(TemplateView):
    template_name = "terminusgps_tracker/dashboard.html"
    http_method_names = ["get"]

    def get_context_data(self) -> dict:
        context = super().get_context_data(self)
        context["services"] = AuthService.objects.all()
