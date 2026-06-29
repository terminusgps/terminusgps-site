from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import models


class CommandExecutionForm(forms.Form):
    command_name = forms.CharField()


class UpdateInstallJobForm(forms.ModelForm):
    class Meta:
        model = models.InstallJob
        fields = [
            "imei",
            "resource",
            "vin",
            "license_plate",
            "mileage",
            "vehicle_id",
        ]


class NewInstallJobForm(forms.ModelForm):
    class Meta:
        model = models.InstallJob
        fields = ["employee", "resource", "imei", "vin"]
        help_texts = {
            "resource": _("Select the company associated with this job.")
        }
        widgets = {
            "resource": forms.widgets.Select(
                attrs={
                    "hx-get": reverse_lazy("installer:select resource"),
                    "hx-target": "this",
                    "hx-trigger": "load once",
                }
            ),
            "imei": forms.widgets.TextInput(
                attrs={"placeholder": "869738060092801"}
            ),
            "vin": forms.widgets.TextInput(
                attrs={"placeholder": "JTHBA30G065155212"}
            ),
        }
