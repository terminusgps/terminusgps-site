from django import forms
from django.urls import reverse_lazy

from . import models


class NewInstallJobForm(forms.ModelForm):
    class Meta:
        model = models.InstallJob
        fields = ["employee", "resource", "imei", "vin"]
        widgets = {
            "resource": forms.widgets.Select(
                attrs={
                    "hx-get": reverse_lazy("installer:select resource"),
                    "hx-target": "this",
                    "hx-trigger": "load once",
                }
            )
        }
