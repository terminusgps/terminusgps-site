from typing import Any

from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.forms import ShippingAddressCreationForm
from terminusgps_tracker.models import TrackerShippingAddress
from terminusgps_tracker.views.mixins import (
    HtmxMixin,
    ProfileContextMixin,
    ProfileRequiredMixin,
)


class ShippingAddressDetailView(
    DetailView, ProfileRequiredMixin, ProfileContextMixin, HtmxMixin
):
    content_type = "text/html"
    context_object_name = "shipping_address"
    http_method_names = ["get"]
    model = TrackerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_detail.html"
    template_name = "terminusgps_tracker/addresses/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        shipping_address: TrackerShippingAddress = self.get_object()
        if self.profile is not None:
            context["default"] = shipping_address.is_default or False
            context["address"] = shipping_address.authorizenet_get_shipping_address(
                self.profile.authorizenet_id, shipping_address.authorizenet_id
            )
        return context


class ShippingAddressCreateView(FormView, ProfileContextMixin, HtmxMixin):
    button_template_name = "terminusgps_tracker/addresses/create_button.html"
    form_class = ShippingAddressCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_url = reverse_lazy("tracker settings")
    template_name = "terminusgps_tracker/addresses/create.html"

    def get_success_url(self, addr: TrackerShippingAddress | None = None) -> str:
        if addr is not None:
            return reverse("shipping detail", kwargs={"pk": addr.pk})
        return str(self.success_url)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.template_name = self.button_template_name
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        if self.profile is not None:
            address = TrackerShippingAddress.objects.create(profile=self.profile)
            address.save(form)
            return HttpResponseRedirect(self.get_success_url(address))
        form.add_error(
            None,
            ValidationError(
                _(
                    "Whoops! Couldn't find a profile for '%(user)s'. Please try again later."
                ),
                code="no_profile",
                params={"user": self.request.user},
            ),
        )
        return self.form_invalid(form=form)


class ShippingAddressDeleteView(DeleteView, ProfileContextMixin, HtmxMixin):
    context_object_name = "shipping_address"
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    model = TrackerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_delete.html"
    permission_denied_message = "Please login and try again."
    queryset = TrackerShippingAddress.objects.none()
    raise_exception = True
    success_url = reverse_lazy("tracker settings")
    template_name = "terminusgps_tracker/addresses/delete.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        addr = self.get_object()
        addr.delete()
        return HttpResponse("", status=200)

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.addresses.all()
        return self.queryset
