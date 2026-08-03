from django import forms
from django.forms.widgets import HiddenInput, NumberInput, TextInput
from django.utils.translation import gettext_lazy as _
from formset.collection import AddSiblingActivator, FormCollection
from formset.renderers.tailwind import FormRenderer

from . import models


class CommandExecutionForm(forms.Form):
    command_name = forms.CharField()


class WialonUnitForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=HiddenInput)

    class Meta:
        model = models.WialonUnit
        fields = ["id", "imei", "vin", "plate", "mileage"]
        help_texts = {
            "imei": _("Provide the tracking device's 5-20 digit IMEI number."),
            "vin": _(
                "Optional. Provide the vehicle's 17-character VIN number."
            ),
            "plate": _("Optional. Provide the vehicle's license plate."),
            "mileage": _("Optional. Provide the vehicle's current mileage."),
        }
        widgets = {
            "imei": TextInput(attrs={"placeholder": "869738060092801"}),
            "vin": TextInput(attrs={"placeholder": "JTHBA30G065155212"}),
            "plate": TextInput(attrs={"placeholder": "LYL1825"}),
            "mileage": NumberInput(),
        }


class WialonUnitCollection(FormCollection):
    legend = _("Units")
    induce_add_sibling = ".add_unit:active"
    related_field = "job"
    unit = WialonUnitForm()
    min_siblings = 1
    add_unit = AddSiblingActivator(add_label=_("Add Unit"))

    def get_or_create_instance(self, data):
        if data := data.get("department"):
            try:
                return self.instance.units.get(id=data.get("id") or 0), False
            except AttributeError, models.WialonUnit.DoesNotExist, ValueError:
                form = WialonUnitForm(data=data)
                if form.is_valid():
                    return models.WialonUnit(
                        imei=form.cleaned_data["imei"],
                        vin=form.cleaned_data.get("vin", ""),
                        plate=form.cleaned_data.get("plate", ""),
                        mileage=form.cleaned_data.get("mileage", 0),
                    ), False
        return None, False


class InstallJobForm(forms.ModelForm):
    class Meta:
        model = models.InstallJob
        fields = ["company", "employee"]


class InstallJobCollection(FormCollection):
    default_renderer = FormRenderer()
    job = InstallJobForm()
    units = WialonUnitCollection()
