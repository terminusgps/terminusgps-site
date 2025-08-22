import decimal
import typing

from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, UpdateView
from terminusgps.authorizenet import subscriptions as anet_subscriptions
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items import WialonObjectFactory
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_unit_by_imei

from terminusgps_tracker.forms import CustomerWialonUnitCreationForm
from terminusgps_tracker.models import (
    Customer,
    CustomerSubscriptionTier,
    CustomerWialonUnit,
)
from terminusgps_tracker.views.mixins import (
    CustomerAuthenticationRequiredMixin,
)


class CustomerWialonUnitCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {
        "title": "Register New Unit",
        "subtitle": "Enter a name and IMEI # for your new unit",
    }
    form_class = CustomerWialonUnitCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/units/partials/_create.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/units/create.html"

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["name"] = f"{self.request.user.first_name}'s Ride"
        return initial

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context

    def form_valid(self, form: CustomerWialonUnitCreationForm) -> HttpResponse:
        imei: str = form.cleaned_data["imei"]
        name: str = form.cleaned_data["name"]
        customer: Customer = Customer.objects.get(user=self.request.user)

        with WialonSession(token=settings.WIALON_TOKEN) as session:
            unit: WialonUnit | None = get_unit_by_imei(imei, session)
            if unit is None or not hasattr(unit, "id"):
                form.add_error(
                    "imei",
                    ValidationError(
                        _(
                            "Whoops! Couldn't find a unit with IMEI # '%(imei)s'."
                        ),
                        code="invalid",
                        params={"imei": form.cleaned_data["imei"]},
                    ),
                )
                return self.form_invalid(form=form)

            if unit.get_name() != name:
                unit.set_name(name)
            CustomerWialonUnit.objects.create(
                id=unit.id,
                customer=customer,
                name=name,
                tier=CustomerSubscriptionTier.objects.first(),
            )
            return HttpResponseRedirect(
                reverse(
                    "tracker:list unit", kwargs={"customer_pk": customer.pk}
                )
            )


class CustomerWialonUnitDetailView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Detail Wialon Unit"}
    http_method_names = ["get"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_detail.html"
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.none()
    template_name = "terminusgps_tracker/units/detail.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return CustomerWialonUnit.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        obj: CustomerWialonUnit = self.get_object()
        if not obj.name:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                factory = WialonObjectFactory(session)
                unit = factory.get("avl_unit", obj.pk)
                obj.name = unit.get_name()
                obj.save()
        return super().get(request, *args, **kwargs)


class CustomerWialonUnitUpdateView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    context_object_name = "unit"
    fields = ["name", "tier"]
    http_method_names = ["get", "post"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_update.html"
    queryset = CustomerWialonUnit.objects.none()
    template_name = "terminusgps_tracker/units/update.html"
    pk_url_kwarg = "unit_pk"

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        form.fields["name"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["tier"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        return form

    def get_success_url(self) -> str:
        return reverse(
            "tracker:detail unit",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "unit_pk": self.kwargs["unit_pk"],
            },
        )

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return CustomerWialonUnit.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("customer")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        obj: CustomerWialonUnit = self.get_object()
        response = super().form_valid(form=form)

        if "name" in form.changed_data:
            new_name: str = form.cleaned_data["name"]
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                factory = WialonObjectFactory(session)
                unit = factory.get("avl_unit", obj.pk)
                unit.set_name(new_name)

        if "tier" in form.changed_data:
            new_amount: decimal.Decimal = obj.customer.get_unit_price_sum()
            anet_subscriptions.update_subscription(
                obj.pk, apicontractsv1.ARBSubscriptionType(amount=new_amount)
            )

        return response


class CustomerWialonUnitListView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "unit_list"
    http_method_names = ["get"]
    model = CustomerWialonUnit
    ordering = "pk"
    paginate_by = 6
    partial_template_name = "terminusgps_tracker/units/partials/_list.html"
    queryset = CustomerWialonUnit.objects.none()
    template_name = "terminusgps_tracker/units/list.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return (
            CustomerWialonUnit.objects.filter(
                customer__pk=self.kwargs["customer_pk"]
            )
            .select_related("customer")
            .order_by(self.get_ordering())
        )
