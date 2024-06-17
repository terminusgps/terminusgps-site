from typing import Optional

from django import forms
from django.utils.translation import gettext_lazy as _

from .wialon.validators import (imei_number_exists_in_db,
                                imei_number_is_unassigned)


def get_form(form_name: str, data: Optional[dict]) -> forms.Form:
    match form_name:
        case "register":
            form = WialonRegistration(data)
        case _:
            raise NotImplementedError

    return form


class WialonRegistration(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=256, initial="First")
    last_name = forms.CharField(label="Last Name", max_length=256, initial="Last")
    email = forms.EmailField(label="Email", max_length=256, initial="Email")
    asset_name = forms.CharField(label="Asset Name", max_length=256, initial="Asset")
    phone_number = forms.CharField(label="Phone", max_length=256, initial="Phone #")
    vin_number = forms.CharField(label="VIN", max_length=17, initial="VIN #")
    imei_number = forms.CharField(
        label="IMEI",
        max_length=20,
        initial="IMEI #",
        validators=[
            imei_number_exists_in_db,
            imei_number_is_unassigned,
        ],
    )

    def action(self) -> str:
        return "/forms/fields"
