from typing import Any
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.validators import (
    validate_asset_name_is_unique,
    validate_imei_number_is_available,
    validate_phone_number,
    validate_street_address,
)


class CountryCode(models.TextChoices):
    UNITED_STATES = "US", _("United States")
    CANADA = "CA", _("Canada")
    MEXICO = "MX", _("Mexico")


class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=64)
    last_name = forms.CharField(label="Last Name", max_length=64)
    phone_number = forms.CharField(label="Phone #", max_length=64)
    email = forms.EmailField(label="Email Address")
    password1 = forms.CharField(label="Password", max_length=32, min_length=8)
    password2 = forms.CharField(label="Confirm Password", max_length=32, min_length=8)

    address_street = forms.CharField(
        label="Street", validators=[validate_street_address]
    )
    address_city = forms.CharField(label="City")
    address_state = forms.CharField(label="State")
    address_zip = forms.CharField(label="Zip")
    address_country = forms.ChoiceField(label="Country", choices=CountryCode.choices)
    address_phone = forms.CharField(label="Phone #", validators=[validate_phone_number])

    def clean(self, **kwargs) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean(**kwargs)
        if cleaned_data:
            password, repeated_password = (
                cleaned_data["password1"],
                cleaned_data["password2"],
            )
            if password != repeated_password:
                self.add_error(
                    "password1",
                    ValidationError(_("Passwords do not match."), code="invalid"),
                )
                self.add_error(
                    "password2",
                    ValidationError(_("Passwords do not match."), code="invalid"),
                )
        return cleaned_data


class CustomerAssetCustomizationForm(forms.Form):
    imei_number = forms.CharField(
        label="IMEI #",
        min_length=1,
        max_length=17,
        validators=[validate_imei_number_is_available],
    )
    asset_name = forms.CharField(
        label="Asset Name",
        min_length=1,
        max_length=64,
        validators=[validate_asset_name_is_unique],
    )
    phone_number = forms.CharField(label="Phone #", min_length=1, max_length=17)


class CustomerCreditCardUploadForm(forms.Form):
    card_number = forms.CharField(label="Card #", min_length=8, max_length=19)
    card_expiry = forms.CharField(label="Card Expiration", min_length=4, max_length=4)
    card_code = forms.CharField(label="Card Security Code", min_length=2, max_length=4)

    address_street = forms.CharField(
        label="Street", validators=[validate_street_address]
    )
    address_city = forms.CharField(label="City")
    address_state = forms.CharField(label="State")
    address_zip = forms.CharField(label="Zip")
    address_country = forms.ChoiceField(label="Country", choices=CountryCode.choices)
    address_phone = forms.CharField(label="Phone #", validators=[validate_phone_number])
