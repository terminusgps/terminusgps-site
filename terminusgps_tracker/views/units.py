from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, UpdateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items import WialonObjectFactory
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
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Wialon Unit"}
    form_class = CustomerWialonUnitCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/units/partials/_create.html"
    template_name = "terminusgps_tracker/units/create.html"

    def get_success_url(self) -> str:
        return reverse(
            "tracker:list unit",
            kwargs={"customer_pk": self.kwargs.get("customer_pk")},
        )

    def form_valid(self, form: CustomerWialonUnitCreationForm) -> HttpResponse:
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            imei = form.cleaned_data["imei"]
            name = form.cleaned_data["name"]
            customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
            unit = get_unit_by_imei(imei, session)

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
            return super().form_valid(form=form)


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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        obj: CustomerWialonUnit = self.get_object()

        if not obj.name:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                factory = WialonObjectFactory(session)
                unit = factory.get(obj.wialon_type, obj.pk)
                obj.name = unit.get_name()
                obj.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return CustomerWialonUnit.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )


class CustomerWialonUnitUpdateView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    context_object_name = "unit"
    fields = ["name"]
    http_method_names = ["get", "post"]
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_update.html"
    queryset = CustomerWialonUnit.objects.none()
    template_name = "terminusgps_tracker/units/update.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return CustomerWialonUnit.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        obj: CustomerWialonUnit = self.get_object()
        new_name: str = form.cleaned_data["new_name"]

        with WialonSession(token=settings.WIALON_TOKEN) as session:
            factory = WialonObjectFactory(session)
            unit = factory.get(obj.wialon_type, obj.pk)
            unit.set_name(new_name)
        return super().form_valid(form=form)


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
        return CustomerWialonUnit.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).order_by(self.get_ordering())
