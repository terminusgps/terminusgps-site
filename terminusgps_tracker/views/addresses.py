from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView

from terminusgps_tracker.forms import ShippingAddressCreationForm
from terminusgps_tracker.models import TrackerShippingAddress
from terminusgps_tracker.views.base import TrackerBaseView


class ShippingAddressDetailView(DetailView, TrackerBaseView, LoginRequiredMixin):
    content_type = "text/html"
    context_object_name = "shipping_address"
    http_method_names = ["get"]
    login_url = reverse_lazy("tracker login")
    model = TrackerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_detail.html"
    permission_denied_message = "Plase login and try again."
    queryset = TrackerShippingAddress.objects.none()
    raise_exception = True
    template_name = "terminusgps_tracker/addresses/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.profile.addresses.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["default"] = self.object.is_default or False
        context["address"] = self.object.authorizenet_get_shipping_address(
            self.profile.authorizenet_id, self.object.authorizenet_id
        )
        return context


class ShippingAddressCreateView(FormView, TrackerBaseView, LoginRequiredMixin):
    button_template_name = "terminusgps_tracker/addresses/create_button.html"
    content_type = "text/html"
    extra_context = {
        "class": "p-4 border border-gray-600 bg-gray-200 rounded flex flex-col gap-4"
    }
    form_class = ShippingAddressCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/addresses/create.html"

    def get_success_url(self, addr: TrackerShippingAddress | None = None) -> str:
        if addr is not None:
            return reverse("detail shipping", kwargs={"pk": addr.pk})
        return str(self.success_url)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.template_name = self.button_template_name
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address = TrackerShippingAddress.objects.create(profile=self.profile)
        address.save(form)
        return HttpResponseRedirect(self.get_success_url(address))


class ShippingAddressDeleteView(DeleteView, TrackerBaseView, LoginRequiredMixin):
    content_type = "text/html"
    context_object_name = "shipping_address"
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    model = TrackerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_delete.html"
    permission_denied_message = "Plase login and try again."
    queryset = TrackerShippingAddress.objects.none()
    raise_exception = True
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/addresses/delete.html"

    def get_queryset(self) -> QuerySet:
        return self.profile.addresses.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**kwargs)
