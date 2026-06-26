from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import models


class CommandExecutionForm(forms.Form):
    command_name = forms.CharField()


AttachmentFormSet = forms.modelformset_factory(
    models.InstallJobAttachment, fields=["job", "file", "note"]
)


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
            )
        }
