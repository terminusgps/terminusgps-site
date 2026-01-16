from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps.wialon.utils import get_unit_from_imei

from .. import models
from ..forms import WialonUnitCreateForm


class WialonUnitCreateView(HtmxTemplateResponseMixin, CreateView):
    content_type = "text/html"
    extra_context = {"title": "Create Unit"}
    form_class = WialonUnitCreateForm
    http_method_names = ["get", "post"]
    model = models.WialonUnit
    template_name = "terminusgps_manager/wialon_units/create.html"

    def form_valid(self, form: WialonUnitCreateForm) -> HttpResponse:
        try:
            customer = models.TerminusGPSCustomer.objects.get(
                user=self.request.user
            )
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                data = get_unit_from_imei(form.cleaned_data["imei"], session)
                unit = form.save(commit=False)
                unit.pk = int(data["id"])
                unit.save(push=True)
                customer.wialon_units.add(unit)
                customer.save(update_fields=["wialon_units"])
                print(f"{customer.wialon_units.count() = }")
                return super().form_valid(form=form)
        except models.TerminusGPSCustomer.DoesNotExist:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! You don't have a customer associated with your account. Please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        except ValueError:
            form.add_error(
                "imei",
                ValidationError(
                    _("Whoops! Couldn't find a unit with IMEI #%(imei)s"),
                    code="invalid",
                    params={"imei": form.cleaned_data["imei"]},
                ),
            )
            return self.form_invalid(form=form)
        except WialonAPIError as error:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"),
                    code="invalid",
                    params={"error": str(error)},
                ),
            )
            return self.form_invalid(form=form)


class WialonUnitListView(HtmxTemplateResponseMixin, ListView):
    allow_empty = True
    content_type = "text/html"
    extra_context = {"title": "Units"}
    http_method_names = ["get"]
    model = models.WialonUnit
    ordering = "name"
    paginate_by = 8
    template_name = "terminusgps_manager/wialon_units/list.html"

    def get_queryset(self) -> QuerySet:
        try:
            return (
                models.TerminusGPSCustomer.objects.get(user=self.request.user)
                .wialon_units.all()
                .order_by(self.get_ordering())
            )
        except models.TerminusGPSCustomer.DoesNotExist:
            return self.model.objects.none()


class WialonUnitDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.WialonUnit
    template_name = "terminusgps_manager/wialon_units/detail.html"

    def get_queryset(self) -> QuerySet:
        try:
            return models.TerminusGPSCustomer.objects.get(
                user=self.request.user
            ).wialon_units.all()
        except models.TerminusGPSCustomer.DoesNotExist:
            return self.model.objects.none()


class WialonUnitUpdateView(HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = models.WialonUnit
    template_name = "terminusgps_manager/wialon_units/update.html"

    def get_queryset(self) -> QuerySet:
        try:
            return models.TerminusGPSCustomer.objects.get(
                user=self.request.user
            ).wialon_units.all()
        except models.TerminusGPSCustomer.DoesNotExist:
            return self.model.objects.none()
