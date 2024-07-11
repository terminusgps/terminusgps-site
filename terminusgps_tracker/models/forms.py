from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from typing import Union

from terminusgps_tracker.wialonapi import WialonSession
from terminusgps_tracker.wialonapi.query import imei_number_exists_in_wialon


def validate_imei_number_exists(value: str) -> None:
    """Checks if the given value is present in the TerminusGPS UUID database."""
    with WialonSession() as session:
        if not imei_number_exists_in_wialon(value, session):
            raise ValidationError(
                _(
                    "IMEI number '%(value)s' does not exist in the TerminusGPS database."
                ),
                params={"value": value},
            )


class RegistrationForm(forms.Form):
    field_template_name = "terminusgps_tracker/forms/field.html"
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
        help_text="Please enter your first name.",
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
        help_text="Please enter your last name.",
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Please enter your email address.",
    )
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        label="Phone #",
        help_text="Please enter your phone number in any format.",
    )
    asset_name = forms.CharField(
        max_length=255,
        required=True,
        label="Asset Name",
        help_text="Please enter a name for your new asset.",
    )
    imei_number = forms.CharField(
        max_length=20,
        required=True,
        disabled=True,
        label="IMEI #",
        help_text="This should've been filled out for you. If not, please contact support@terminusgps.com",
        validators=[
            validate_imei_number_exists,
        ],
    )

    def send_creds_email(self, to_addr: Union[list[str], str]) -> None:
        """Sends this form's credentials via email to the given address(es)."""

    def get_absolute_url(self):
        return reverse("/forms/registration/", kwargs={"pk": self.pk})
