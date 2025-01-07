from django import forms
from django.forms import widgets

from terminusgps_tracker.validators import (
    validate_wialon_unit_name,
    validate_wialon_imei_number,
)

from terminusgps_tracker.models import TrackerAsset, TrackerAssetCommand


class CommandExecutionForm(forms.Form):
    command = forms.ModelChoiceField(queryset=TrackerAssetCommand.objects.all())


class TrackerAssetUpdateForm(forms.ModelForm):
    class Meta:
        base_class = "p-2 bg-gray-200 text-gray-800 rounded border-gray-600 placeholder-gray-400 valid:border-green-600 invalid:border-red-600 valid:bg-green-100 invalid:bg-red-100"
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "placeholder": "My Vehicle",
                    "class": base_class,
                    "pattern": "[A-Za-z0-9' ]+",
                }
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": base_class + " hover:cursor-not-allowed select-all",
                    "disabled": True,
                }
            ),
        }


class TrackerAssetCreateForm(forms.ModelForm):
    class Meta:
        base_class = (
            "p-2 bg-gray-300 text-gray-800 rounded border-gray-600 placeholder-gray-400"
        )
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={"placeholder": "My Vehicle", "class": base_class}
            ),
            "imei_number": widgets.TextInput(
                attrs={"placeholder": "IMEI #", "class": base_class}
            ),
        }


class AssetUpdateForm(forms.Form):
    name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=widgets.TextInput(
            {"placeholder": "My Vehicle", "class": "p-2 bg-gray-300 text-gray-700"}
        ),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=widgets.NumberInput(
            {"placeholder": "IMEI #", "class": "p-2 bg-gray-300 text-gray-700"}
        ),
        min_length=15,
        max_length=24,
    )


class AssetDeletionForm(forms.Form):
    asset = forms.ModelChoiceField(queryset=TrackerAsset.objects.all())
