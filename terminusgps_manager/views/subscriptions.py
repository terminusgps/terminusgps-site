import typing

from django import forms
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerProfile, Subscription

from ..forms import SubscriptionCreateForm
from ..models import TerminusGPSCustomer


class SubscriptionCreateView(HtmxTemplateResponseMixin, CreateView):
    content_type = "text/html"
    form_class = SubscriptionCreateForm
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_manager/subscriptions/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )
        self.cprofile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = self.cprofile
        return context

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        sub = form.save(commit=False)
        sub.name = "Terminus GPS Subscription"
        sub.amount = self.customer.grand_total
        sub.cprofile = self.cprofile
        sub.save()
        self.customer.sub = sub
        self.customer.save(update_fields=["subscription"])
        return HttpResponseRedirect(
            reverse(
                "terminusgps_manager:detail subscriptions",
                kwargs={"subscription_pk": sub.pk},
            )
        )


class SubscriptionDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/detail.html"


class SubscriptionUpdateView(HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    fields = ["aprofile", "pprofile"]
    http_method_names = ["get", "post"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_manager/subscriptions/update.html"


class SubscriptionDeleteView(HtmxTemplateResponseMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = Subscription
    pk_url_kwarg = "subscription_pk"
    success_url = reverse_lazy("terminusgps_manager:create subscriptions")
