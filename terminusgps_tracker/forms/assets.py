from typing import Any

from django import forms
from django.forms import ValidationError, widgets
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models import TrackerAsset


class TrackerAssetUpdateForm(forms.ModelForm):
    class Meta:
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "placeholder": "My Vehicle",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded invalid:border-terminus-red-600",
                    "required": True,
                }
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded invalid:border-terminus-red-600",
                    "disabled": True,
                }
            ),
        }

    def clean_imei_number(self, value: Any) -> str:
        if value is None:
            raise ValidationError(
                _("IMEI # is required, got '%(value)s'."),
                code="invalid",
                params={"value": value},
            )
        return str(value)

    def clean(self, **kwargs) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean(**kwargs)
        if cleaned_data and cleaned_data.get("name") is None:
            cleaned_data["name"] = cleaned_data["imei_number"]
        return cleaned_data


class TrackerAssetCreateForm(forms.ModelForm):
    class Meta:
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "placeholder": "My Vehicle",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                    "autocomplete": "false",
                }
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                    "autocomplete": "false",
                }
            ),
        }


class AssetDeletionForm(forms.Form):
    asset = forms.ModelChoiceField(queryset=TrackerAsset.objects.all())
