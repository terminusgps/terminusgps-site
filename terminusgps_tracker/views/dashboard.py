from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/dashboard.html"
    extra_context = {"title": "Dashboard", "client_name": settings.CLIENT_NAME}
