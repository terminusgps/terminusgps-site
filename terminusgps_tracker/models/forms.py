import string

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.query import imei_number_exists_in_wialon

def validate_imei_number_exists(value: str) -> None:
    """Checks if the given value is present in the TerminusGPS database."""
    with WialonSession() as session:
        if not imei_number_exists_in_wialon(value, session):
            raise ValidationError(
                _("IMEI number '%(value)s' does not exist in the TerminusGPS database."),
                params={"value": value},
            )

def validate_is_digit(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(_("'%(value)s' can only contain digits."), params={"value": value})

def validate_contains_uppercase(value: str) -> None:
    if not any(c in string.ascii_uppercase for c in value):
        raise ValidationError(_("Must contain at least one uppercase letter."))

def validate_contains_lowercase(value: str) -> None:
    if not any(c in string.ascii_lowercase for c in value):
        raise ValidationError(_("Must contain at least one lowercase letter."))

def validate_contains_digit(value: str) -> None:
    if not any(c in string.digits for c in value):
        raise ValidationError(_("Must contain at least one digit."),)

def validate_contains_special_char(value: str) -> None:
    valid_special_chars = set("!#$%-.:;@?_~")
    if not any(c in valid_special_chars for c in value):
        raise ValidationError(
            _("Must contain at least one special symbol. Symbols: '%(symbols)s'"),
            params={"symbols": "".join(valid_special_chars)}
        )


class PersonForm(forms.Form):
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

class ContactForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Please enter your email address.",
        validators=[validate_email]
    )
    phone_number = forms.CharField(
        required=True,
        label="Phone #",
        help_text="Please enter your phone number.",
    )

class AssetForm(forms.Form):
    imei_number = forms.CharField(
        required=True,
        label="IMEI #",
        help_text="This should've been filled out for you. If not, please contact support@terminusgps.com",
        disabled=True,
        validators=[
            validate_is_digit,
            validate_imei_number_exists,
       ],
    )
    asset_name = forms.CharField(
        max_length=255,
        required=True,
        label="Asset Name",
        help_text="Please enter a name for your new asset.",
    )
    wialon_password = forms.CharField(
        max_length=64,
        min_length=8,
        required=True,
        label="Wialon Password",
        widget=forms.PasswordInput(),
        validators=[
            validate_contains_uppercase,
            validate_contains_lowercase,
            validate_contains_digit,
            validate_contains_special_char,
        ],
    )
    wialon_password_confirmation = forms.CharField(
        max_length=64,
        min_length=8,
        required=True,
        label="Confirm Wialon Password",
        widget=forms.PasswordInput(),
        validators=[
            validate_contains_uppercase,
            validate_contains_lowercase,
            validate_contains_digit,
            validate_contains_special_char,
        ],
    )


class RegistrationForm(PersonForm, ContactForm, AssetForm):
    field_order = [
        "first_name",
        "last_name",
        "asset_name",
        "imei_number",
        "email",
        "wialon_password",
        "wialon_password_confirmation",
    ]

    phone_number = None

    def clean(self) -> dict:
        print("RegistrationForm.clean called")
        cleaned_data = super(RegistrationForm, self).clean()
        print(f"Before logic: {cleaned_data = }")
        if "wialon_password" and "wialon_password_confirmation" in cleaned_data:
            password_1 = cleaned_data["wialon_password"]
            password_2 = cleaned_data["wialon_password_confirmation"]
            if password_1 != password_2:
                self.add_error("wialon_password", "Passwords do not match.")
                self.add_error("wialon_password_confirmation", "Passwords do not match.")

            if "email" in cleaned_data:
                if password_1 == cleaned_data["email"]:
                    self.add_error("wialon_password", "Password cannot be equal to email.")
                if password_2 == cleaned_data["email"]:
                    self.add_error("wialon_password_confirmation", "Password cannot be equal to email.")

        print(f"After logic: {cleaned_data = }")
        return cleaned_data

    def get_absolute_url(self):
        print("RegistrationForm.get_absolute_url called")
        return reverse("/forms/registration/", kwargs={"pk": self.pk})

    def clean_imei_number(self) -> str:
        print("RegistrationForm.clean_imei_number called")
        imei_number = self.cleaned_data.get("imei_number")
        if not imei_number:
            self.add_error("imei_number", "This field is required.")
        if not imei_number.isdigit():
            self.add_error("imei_number", "IMEI # can only contain digits.")
        if len(imei_number) > 20:
            self.add_error("imei_number", "IMEI # must be less than 20 chars.")
        if len(imei_number) < 12:
            self.add_error("imei_number", "IMEI # must be greater than 12 chars.")
        return imei_number
