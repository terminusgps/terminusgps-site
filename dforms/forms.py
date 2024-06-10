from django import forms
from django.core.exceptions import ValidationError
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


def validate_phone_number(value):
    if not value.startswith("+"):
        raise ValidationError(
            _("Phone number must start with a '+'"), code="no_country_code"
        )

    if not value.replace("+", "").isdigit():
        raise ValidationError(
            _("Phone number must contain only digits and country code"),
            code="not_digits",
        )


class MultiPhoneNumberField(forms.Field):
    def to_python(self, value):
        """Normalize the string into a list of phone numbers."""
        if not value:
            return []
        return value.split(",")

    def validate(self, value):
        super().validate(value)
        for num in value:
            validate_phone_number(num)
