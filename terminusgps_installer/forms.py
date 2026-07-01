from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import models
from .validators import validate_imei, validate_is_digit


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
    imei = forms.CharField(
        min_length=5,
        max_length=20,
        validators=[validate_is_digit, validate_imei],
        help_text=_(
            "Provide the 5-20 digit IMEI number present on the GPS tracking device. Ex: 869738060092801"
        ),
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "869738060092801"}
        ),
    )

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
            "vin": forms.widgets.TextInput(
                attrs={"placeholder": "JTHBA30G065155212"}
            ),
        }
