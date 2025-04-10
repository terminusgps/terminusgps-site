from django import forms
from terminusgps.validators import validate_vin_number

from terminusgps_install.models import WialonAccount, WialonAsset


class WialonAssetCreateForm(forms.Form):
    name = forms.CharField(
        label="Unit Name",
        max_length=128,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                "placeholder": "My Vehicle",
            }
        ),
    )
    vin_number = forms.CharField(
        label="VIN #",
        max_length=17,
        validators=[validate_vin_number],
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                "placeholder": "AA0AAAA0AAA000000",
            }
        ),
    )
    account = forms.ModelChoiceField(
        label="Wialon Account",
        queryset=WialonAccount.objects.all().order_by("name"),
        widget=forms.widgets.Select(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300"
            }
        ),
    )


class WialonAssetUpdateForm(forms.ModelForm):
    class Meta:
        model = WialonAsset
        fields = ["name"]
