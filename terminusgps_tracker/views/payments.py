from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, View, DetailView

from terminusgps_tracker.forms import PaymentMethodCreationForm
from terminusgps_tracker.models import TrackerPaymentMethod, TrackerProfile


class InvalidPromptError(Exception):
    """Raised when a provided HX-Prompt is invalid."""


class PaymentMethodDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    context_object_name = "payment"
    http_method_names = ["get", "delete"]
    login_url = reverse_lazy("tracker login")
    model = TrackerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_detail.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    template_name = "terminusgps_tracker/payments/detail.html"
    queryset = TrackerPaymentMethod.objects.none()

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_object(self, queryset: QuerySet | None = None) -> TrackerPaymentMethod:
        return self.profile.payments.filter().get(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        payment_method = self.get_object()
        context["payment"] = self.authorizenet_get_payment_profile(
            self.profile.authorizenet_id, payment_method.authorizenet_id
        )
        context["is_default"] = payment_method.is_default or False
        return context

    @staticmethod
    def authorizenet_get_payment_profile(
        profile_id: int, payment_id: int
    ) -> dict[str, Any]:
        payment = TrackerPaymentMethod.authorizenet_get_payment_profile(
            profile_id=profile_id, payment_id=payment_id
        )
        return payment


class PaymentMethodCreateView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    extra_context = {"title": "New Payment"}
    form_class = PaymentMethodCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/payments/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_message = "Card ending in '%(last_4)s' was added successfully."
    template_name = "terminusgps_tracker/payments/create.html"
    success_url = reverse_lazy("tracker settings")

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % {
            "last_4": cleaned_data["credit_card_number"][-4:]
        }

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        self.template_name = "terminusgps_tracker/payments/create_button.html"
        return self.render_to_response(context=self.get_context_data())

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_template_name

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        payment_profile = TrackerPaymentMethod.objects.create(profile=self.profile)
        payment_profile.save(form)
        return super().form_valid(form=form)


class PaymentMethodDeleteView(LoginRequiredMixin, View):
    http_method_names = ["delete"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.htmx_request = bool(request.headers.get("HX-Request"))
        self.htmx_prompt = request.headers.get("HX-Prompt")

    def delete(self, request: HttpRequest, id: str) -> HttpResponse:
        try:
            assert self.htmx_request
            assert self.htmx_prompt

            last_4 = str(
                TrackerPaymentMethod.authorizenet_get_payment_profile(
                    profile_id=self.profile.authorizenet_id, payment_id=int(id)
                )["payment"]["creditCard"]["cardNumber"]
            )[-4:]
            if self.htmx_prompt != last_4:
                raise InvalidPromptError()

            payment = self.profile.payments.get(authorizenet_id=int(id))
            payment.delete()
        except AssertionError:
            return HttpResponse(status=403)
        except InvalidPromptError:
            return HttpResponse(status=406)
        else:
            return HttpResponse("", status=200)
