import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.constants import (
    ACCESSMASK_UNIT_BASIC,
    ACCESSMASK_UNIT_MIGRATION,
)
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps.wialon.utils import get_unit_from_imei

from ..forms import WialonUnitCreateForm
from ..models import TerminusGPSCustomer, WialonUnit, WialonUser


class UnitNotFoundError(Exception):
    """Raised when a Wialon unit wasn't found."""


class WialonUnitCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_manager/units/create.html"
    form_class = WialonUnitCreateForm
    success_url = reverse_lazy("terminusgps_manager:list units")

    @typing.override
    @transaction.atomic
    def form_valid(self, form: WialonUnitCreateForm) -> HttpResponse:
        try:
            customer = TerminusGPSCustomer.objects.get(user=self.request.user)
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                resp = get_unit_from_imei(form.cleaned_data["imei"], session)
                unit_pk = int(resp["id"])
                super_user, created = WialonUser.objects.get_or_create(
                    id=customer.wialon_account.crt
                )
                super_user.update_access(
                    session, id=unit_pk, access_mask=ACCESSMASK_UNIT_MIGRATION
                )
                customer.wialon_account.migrate(session, id=unit_pk)
                customer.wialon_user.update_access(
                    session, id=unit_pk, access_mask=ACCESSMASK_UNIT_BASIC
                )

                if form.cleaned_data.get("name"):
                    session.wialon_api.item_update_name(
                        **{
                            "itemId": unit_pk,
                            "name": form.cleaned_data["name"],
                        }
                    )

                unit = WialonUnit()
                unit.pk = unit_pk
                unit.save()
                customer.wialon_units.add(unit)
                customer.save()
                return HttpResponseRedirect(
                    reverse("terminusgps_manager:list units")
                )
        except TerminusGPSCustomer.DoesNotExist:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Something went wrong. Please try again later."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        except ValueError:
            form.add_error(
                "imei",
                ValidationError(
                    _("Whoops! Couldn't find a unit with IMEI #%(imei)s."),
                    code="invalid",
                    params={"imei": form.cleaned_data["imei"]},
                ),
            )
            return self.form_invalid(form=form)
        except WialonAPIError as error:
            match error.code:
                case 2004:
                    msg = _(
                        "You can't add units while your account is disabled."
                    )
                    field = None
                    params = None
                case 2008:
                    msg = _(
                        "Unit with IMEI #%(imei)s has already been registered."
                    )
                    field = "imei"
                    params = {"imei": form.cleaned_data["imei"]}
                case _:
                    msg = str(error)
                    field = None
                    params = None

            form.add_error(
                field,
                ValidationError(
                    f"{error.code}: {msg}", code="invalid", params=params
                ),
            )
            return self.form_invalid(form=form)


class WialonUnitListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = WialonUnit
    ordering = "name"
    template_name = "terminusgps_manager/units/list.html"

    def get_queryset(self) -> QuerySet:
        customer, created = TerminusGPSCustomer.objects.get_or_create(
            user=self.request.user
        )
        return customer.wialon_units.all()
