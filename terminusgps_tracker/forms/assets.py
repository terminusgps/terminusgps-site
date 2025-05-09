from django import forms
from django.conf import settings
from terminusgps.wialon.validators import validate_vin_number

from terminusgps_tracker.validators import validate_wialon_imei_number_available


class CustomerAssetCreateForm(forms.Form):
    name = forms.CharField(
        label="Asset Name",
        widget=forms.widgets.TextInput(
            attrs={"class": settings.DEFAULT_FIELD_CLASS, "placeholder": "My Vehicle"}
        ),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number_available],
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "867730050855555",
            }
        ),
    )


class InstallerAssetCreateForm(forms.Form):
    vin_number = forms.CharField(
        label="VIN #",
        validators=[validate_vin_number],
        widget=forms.widgets.TextInput(attrs={"class": settings.DEFAULT_FIELD_CLASS}),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        widget=forms.widgets.TextInput(attrs={"class": settings.DEFAULT_FIELD_CLASS}),
    )
