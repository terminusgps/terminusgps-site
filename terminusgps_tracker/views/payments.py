from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, FormView, DetailView

from terminusgps_tracker.forms import PaymentMethodCreationForm
from terminusgps_tracker.models import TrackerPaymentMethod
from terminusgps_tracker.views.mixins import HtmxMixin, ProfileContextMixin


class InvalidPromptError(Exception):
    """Raised when a provided HX-Prompt is invalid."""


class PaymentMethodDetailView(DetailView, ProfileContextMixin, HtmxMixin):
    content_type = "text/html"
    context_object_name = "payment_method"
    http_method_names = ["get"]
    login_url = reverse_lazy("tracker login")
    model = TrackerPaymentMethod
    partial_template_name = "terminusgps_tracker/payments/partials/_detail.html"
    permission_denied_message = "Please login and try again."
    queryset = TrackerPaymentMethod.objects.none()
    raise_exception = True
    template_name = "terminusgps_tracker/payments/detail.html"

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.payments.all()
        return self.queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        payment_method: TrackerPaymentMethod = self.get_object()
        if self.profile is not None:
            context["default"] = payment_method.is_default or False
            context["payment"] = payment_method.authorizenet_get_payment_profile(
                self.profile.authorizenet_id, payment_method.authorizenet_id
            )
        return context

    @staticmethod
    def get_last_4(payment: dict) -> str:
        return payment["payment"]["creditCard"]["cardNumber"][-4:]


class PaymentMethodCreateView(FormView, ProfileContextMixin, HtmxMixin):
    button_template_name = "terminusgps_tracker/payments/create_button.html"
    extra_context = {
        "title": "New Payment",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    form_class = PaymentMethodCreationForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/payments/partials/_create.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    success_url = reverse_lazy("settings")
    template_name = "terminusgps_tracker/payments/create.html"

    def get_success_url(
        self, payment_method: TrackerPaymentMethod | None = None
    ) -> str:
        if payment_method is not None:
            return reverse("detail payment", kwargs={"pk": payment_method.pk})
        return str(self.success_url)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.template_name = self.button_template_name
        return self.render_to_response(context=self.get_context_data())

    def form_valid(self, form: PaymentMethodCreationForm) -> HttpResponse:
        if self.profile is not None:
            payment_method = TrackerPaymentMethod.objects.create(profile=self.profile)
            payment_method.save(form)
            return HttpResponseRedirect(self.get_success_url(payment_method))
        form.add_error(
            None,
            ValidationError(
                _("Whoops! Couldn't find your profile, please try again later."),
                code="no_profile",
            ),
        )
        return self.form_invalid(form=form)


class PaymentMethodDeleteView(DeleteView, ProfileContextMixin, HtmxMixin):
    context_object_name = "payment_method"
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/payments/partials/_delete.html"
    permission_denied_message = "Please login and try again."
    raise_exception = True
    template_name = "terminusgps_tracker/payments/delete.html"
    model = TrackerPaymentMethod
    queryset = TrackerPaymentMethod.objects.none()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            assert self.profile is not None, "No profile was set"
            assert request.headers.get("HX-Request")
            assert request.headers.get("HX-Prompt")
        except AssertionError:
            return HttpResponse(status=403)

        payment_method = self.get_object()
        last_4 = str(
            TrackerPaymentMethod.authorizenet_get_payment_profile(
                profile_id=self.profile.authorizenet_id,
                payment_id=payment_method.authorizenet_id,
            )["payment"]["creditCard"]["cardNumber"]
        )[-4:]
        if last_4 == request.headers.get("HX-Prompt"):
            payment_method.delete()
            return HttpResponse("", status=200)
        return HttpResponse(status=406)

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.payments.all()
        return self.queryset
