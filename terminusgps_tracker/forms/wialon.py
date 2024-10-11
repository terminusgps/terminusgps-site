from django import forms

from terminusgps_tracker.validators import (
    validate_asset_name_is_unique,
    validate_imei_number_exists,
)


class AssetCustomizationForm(forms.Form):
    imei_number = forms.CharField(
        label="Asset IMEI #",
        max_length=17,
        required=True,
        validators=[validate_imei_number_exists],
    )
    asset_name = forms.CharField(
        label="Asset Name",
        max_length=64,
        required=True,
        validators=[validate_asset_name_is_unique],
    )
