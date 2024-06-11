from django import forms
from django.utils.translation import gettext_lazy as _

from .wialon.validators import (imei_number_exists_in_db,
                                imei_number_is_unassigned)


class WialonRegistration(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=256)
    last_name = forms.CharField(label="Last Name", max_length=256)
    email = forms.EmailField(label="Email", max_length=256)
    asset_name = forms.CharField(label="Asset Name", max_length=256)
    phone_number = forms.CharField(label="Phone Number", max_length=256)
    vin_number = forms.CharField(label="VIN #", max_length=17)
    imei_number = forms.CharField(
        label="IMEI #",
        max_length=20,
        validators=[
            imei_number_exists_in_db,
            imei_number_is_unassigned,
        ],
    )
