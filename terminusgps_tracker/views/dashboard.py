from django.db.models.query import QuerySet
from django.views.generic import TemplateView

from terminusgps_tracker.models.token import AuthToken


class DashboardView(TemplateView):
    template_name = "terminusgps_tracker/dashboard.html"
    http_method_names = ["get"]

    def get_tokens(self) -> QuerySet:
        return AuthToken.objects.filter(user=self.request.user).all()
