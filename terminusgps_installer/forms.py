from django import forms
from django.forms import widgets
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import models


class NewInstallJobForm(forms.ModelForm):
    class Meta:
        model = models.InstallJob
        fields = ["installer", "resource", "imei", "vin"]
        help_texts = {
            "installer": _(
                "Select the installer responsible for this job from the list."
            ),
            "resource": _(
                "Select a Wialon resource from the list. Click then start typing to bubble options up to the top."
            ),
            "imei": _("Enter the IMEI number on the GPS tracking device."),
            "vin": _("Optional. Enter the vehicle's 17-digit VIN number."),
            "mileage": _("Optional. Enter the vehicle's current mileage."),
            "license": _("Optional. Enter the vehicle's license plate."),
        }
        widgets = {
            "resource": widgets.Select(
                attrs={
                    "hx-get": reverse_lazy("installer:select resource"),
                    "hx-target": "this",
                    "hx-trigger": "load once",
                    "hx-indicator": "#loading",
                }
            ),
            "vin": widgets.TextInput(
                attrs={
                    "hx-get": reverse_lazy("installer:vin info"),
                    "hx-target": "#id_vin_info",
                    "hx-trigger": "input changed delay:300ms",
                    "hx-indicator": "#loading",
                }
            ),
        }
