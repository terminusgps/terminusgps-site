from typing import Any

from authorizenet.apicontractsv1 import customerAddressType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView

from terminusgps.authorizenet.profiles.addresses import AddressProfile
from terminusgps_tracker.forms import ShippingAddressCreationForm
from terminusgps_tracker.models import TrackerShippingAddress
from terminusgps_tracker.models.profiles import TrackerProfile
from terminusgps_tracker.views.base import TrackerBaseView


class ShippingAddressDetailView(LoginRequiredMixin, DetailView, TrackerBaseView):
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
        context["default"] = self.object.default
        context["address"] = self.object.address_profile.get_details().address
        return context


class ShippingAddressCreateView(LoginRequiredMixin, FormView, TrackerBaseView):
    button_template_name = "terminusgps_tracker/addresses/create_button.html"
    content_type = "text/html"
    extra_context = {
        "class": "p-4 border border-gray-600 bg-gray-200 rounded grid grid-cols-1 md:grid-cols-2 gap-2"
    }
    form_class = ShippingAddressCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/addresses/create.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.template_name = self.button_template_name
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address = TrackerShippingAddress.objects.create(profile=self.profile)
        address.save(form)
        return super().form_valid(form=form)


class ShippingAddressDeleteView(LoginRequiredMixin, DeleteView, TrackerBaseView):
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

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        shipping_address = self.get_object()
        shipping_address.delete()
        return self.render_to_response(context=self.get_context_data())

    def get_queryset(self) -> QuerySet:
        return self.profile.addresses.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**kwargs)
