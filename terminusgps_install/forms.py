from django import forms
from terminusgps.validators import validate_vin_number

from terminusgps_install.models import WialonAsset


class WialonAssetCreateForm(forms.Form):
    name = forms.CharField(max_length=128)
    vin_number = forms.CharField(max_length=17, validators=[validate_vin_number])
    account = forms.HiddenInput()


class WialonAssetUpdateForm(forms.ModelForm):
    class Meta:
        model = WialonAsset
        fields = ["name"]
