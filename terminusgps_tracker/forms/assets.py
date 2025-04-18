from django import forms
from django.contrib.auth import get_user_model
from terminusgps.wialon.validators import validate_vin_number

default_field_class = "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"


class CustomerAssetCreateForm(forms.Form):
    name = forms.CharField(
        label="Asset Name",
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "My Vehicle"}
        ),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "867730050855555"}
        ),
    )


class InstallerAssetCreateForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(), widget=forms.widgets.HiddenInput()
    )
    vin_number = forms.CharField(
        label="VIN #",
        validators=[validate_vin_number],
        widget=forms.widgets.TextInput(attrs={"class": default_field_class}),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        widget=forms.widgets.TextInput(attrs={"class": default_field_class}),
    )
