from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, View

from terminusgps_tracker.forms import ShippingAddressCreationForm
from terminusgps_tracker.models import TrackerProfile, TrackerShippingAddress


class ShippingAddressDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    context_object_name = "address"
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_detail.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    template_name = "terminusgps_tracker/addresses/detail.html"
    model = TrackerShippingAddress
    queryset = TrackerShippingAddress.objects.none()

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_object(self, queryset: QuerySet | None = None) -> TrackerShippingAddress:
        return self.profile.addresses.get(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        shipping_address = self.get_object()
        context["address"] = self.authorizenet_get_shipping_address(
            self.profile.authorizenet_id, shipping_address.authorizenet_id
        )
        context["is_default"] = shipping_address.is_default or False
        return context

    @staticmethod
    def authorizenet_get_shipping_address(
        profile_id: int, address_id: int
    ) -> dict[str, Any]:
        address = TrackerShippingAddress.authorizenet_get_shipping_address(
            profile_id=profile_id, address_id=address_id
        )
        return address


class ShippingAddressCreateView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    form_class = ShippingAddressCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/addresses/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_message = "'%(addr)s' was added successfully."
    success_url = reverse_lazy("tracker settings")
    template_name = "terminusgps_tracker/addresses/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_template_name

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % {"addr": cleaned_data.get("address_street", "")}

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        self.template_name = "terminusgps_tracker/addresses/create_button.html"
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: ShippingAddressCreationForm) -> HttpResponse:
        address = TrackerShippingAddress.objects.create(profile=self.profile)
        address.save(form)
        return super().form_valid(form=form)


class ShippingAddressDeleteView(LoginRequiredMixin, View):
    http_method_names = ["delete"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.htmx_request = bool(request.headers.get("HX-Request"))

    def delete(self, request: HttpRequest, id: str) -> HttpResponse:
        if not self.htmx_request:
            return HttpResponse(status=403)
        address = self.profile.addresses.get(authorizenet_id=int(id))
        address.delete()
        return HttpResponse("", status=200)
