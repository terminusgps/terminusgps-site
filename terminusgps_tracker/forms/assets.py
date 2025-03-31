from django import forms

from terminusgps_tracker.models import Customer
from terminusgps_tracker.validators import (
    validate_wialon_imei_number_available,
    validate_wialon_unit_name_unique,
)


class CustomerAssetCreateForm(forms.Form):
    default_field_class = "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
    name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name_unique],
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "My Vehicle"}
        ),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number_available],
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "867730050855555"}
        ),
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(), widget=forms.widgets.HiddenInput()
    )
