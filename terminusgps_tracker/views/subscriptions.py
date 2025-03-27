from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import DetailView

from terminusgps_tracker.models import Customer, Subscription
from terminusgps_tracker.views.mixins import HtmxTemplateResponseMixin


class SubscriptionDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get", "patch"]
    login_url = reverse_lazy("login")
    model = Subscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_detail.html"
    permission_denied_message = "Please login and try again."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/detail.html"
    extra_context = {"class": "flex flex-col gap-4 border p-4 rounded bg-white"}

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer = Customer.objects.get(user=request.user)

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return self.model._default_manager.all().filter(customer=self.customer)
