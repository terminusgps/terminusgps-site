from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView

from terminusgps_tracker.forms import ShippingAddressCreationForm
from terminusgps_tracker.models import TrackerProfile, TrackerShippingAddress


class ShippingAddressDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    context_object_name = "shipping_address"
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_detail.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    template_name = "terminusgps_tracker/addresses/detail.html"
    model = TrackerShippingAddress
    queryset = TrackerShippingAddress.objects.none()
    http_method_names = ["get"]

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.addresses.all()
        return self.queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        shipping_address: TrackerShippingAddress = self.get_object()
        if self.profile is not None:
            context["default"] = shipping_address.is_default or False
            context["address"] = shipping_address.authorizenet_get_shipping_address(
                self.profile.authorizenet_id, shipping_address.authorizenet_id
            )
        return context

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user is not None and request.user.is_authenticated
            else None
        )
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name


class ShippingAddressCreateView(LoginRequiredMixin, FormView):
    form_class = ShippingAddressCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_url = reverse_lazy("tracker settings")
    template_name = "terminusgps_tracker/addresses/create.html"
    button_template_name = "terminusgps_tracker/addresses/create_button.html"

    def get_success_url(self, addr: TrackerShippingAddress | None = None) -> str:
        if addr is not None:
            return reverse("shipping detail", kwargs={"pk": addr.pk})
        return str(self.success_url)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        self.template_name = self.button_template_name
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address = TrackerShippingAddress.objects.create(profile=self.profile)
        address.save(form)
        return super().form_valid(form=form)


class ShippingAddressDeleteView(LoginRequiredMixin, DeleteView):
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    model = TrackerShippingAddress
    partial_template_name = "terminusgps_tracker/addresses/partials/_delete.html"
    permission_denied_message = "Please login and try again."
    queryset = TrackerShippingAddress.objects.none()
    raise_exception = True
    success_url = reverse_lazy("tracker settings")
    template_name = "terminusgps_tracker/addresses/delete.html"
    context_object_name = "shipping_address"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        addr = self.get_object()
        addr.delete()
        return HttpResponse("", status=200)

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.addresses.all()
        return self.queryset

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user is not None and request.user.is_authenticated
            else None
        )
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name
