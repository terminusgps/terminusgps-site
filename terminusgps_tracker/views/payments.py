from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, DetailView

from terminusgps_tracker.forms.payments import PaymentMethodCreationForm
from terminusgps_tracker.models import TrackerPaymentMethod
from terminusgps_tracker.views.base import TrackerBaseView


class PaymentMethodCreateView(LoginRequiredMixin, FormView, TrackerBaseView):
    button_template_name = "terminusgps_tracker/payments/create_button.html"
    content_type = "text/html"
    extra_context = {
        "class": "p-4 border border-gray-600 bg-gray-200 rounded grid grid-cols-1 md:grid-cols-2 gap-2"
    }
    form_class = PaymentMethodCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/payments/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/payments/create.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.template_name = self.button_template_name
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        payment_method = TrackerPaymentMethod.objects.create(profile=self.profile)
        payment_method.save(form)
        return super().form_valid(form=form)


class PaymentMethodDetailView(LoginRequiredMixin, DetailView, TrackerBaseView):
    content_type = "text/html"
    context_object_name = "payment_obj"
    http_method_names = ["get"]
    login_url = reverse_lazy("tracker login")
    model = TrackerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_detail.html"
    permission_denied_message = "Plase login and try again."
    queryset = TrackerPaymentMethod.objects.none()
    raise_exception = True
    template_name = "terminusgps_tracker/payments/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.profile.payments.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["default"] = self.object.default
        context["payment"] = self.object.payment_profile.get_details().paymentProfile
        return context


class PaymentMethodDeleteView(LoginRequiredMixin, DeleteView, TrackerBaseView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    model = TrackerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_delete.html"
    permission_denied_message = "Plase login and try again."
    queryset = TrackerPaymentMethod.objects.none()
    raise_exception = True
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/payments/delete.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        payment_method = self.get_object()
        payment_method.delete()
        return self.render_to_response(context=self.get_context_data())

    def get_queryset(self) -> QuerySet:
        return self.profile.payments.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**kwargs)
