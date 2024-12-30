from django import forms
from django.forms import widgets

from terminusgps_tracker.validators import (
    validate_wialon_unit_name,
    validate_wialon_imei_number,
    validate_phone,
)

from terminusgps_tracker.models import TrackerAsset, TrackerAssetCommand


class CommandExecutionForm(forms.Form):
    command = forms.ModelChoiceField(queryset=TrackerAssetCommand.objects.all())


class AssetCreationForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=widgets.TextInput(
            attrs={
                "class": "w-full block mb-4 mt-2 p-2 rounded-md",
                "placeholder": "My Vehicle",
                "autofocus": True,
            }
        ),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=widgets.NumberInput(
            attrs={
                "placeholder": "355197370064417",
                "class": "w-full block mb-4 mt-2 p-2 rounded-md",
            }
        ),
        min_length=15,
        max_length=24,
    )


class AssetModificationForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=widgets.TextInput({"placeholder": "My Vehicle"}),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=widgets.NumberInput({"placeholder": "123412341234"}),
        min_length=15,
        max_length=24,
    )
    phone_number = forms.CharField(
        label="Phone #",
        validators=[validate_phone],
        widget=widgets.TextInput({"placeholder": "(555) 555-5555"}),
        min_length=12,
        max_length=19,
    )


class AssetDeletionForm(forms.Form):
    asset = forms.ModelChoiceField(queryset=TrackerAsset.objects.all())
