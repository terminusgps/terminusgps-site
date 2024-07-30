import string

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.wialonapi.query import (imei_number_exists_in_wialon,
                                                 imei_number_is_unregistered)
from terminusgps_tracker.wialonapi.session import WialonSession


def get_initial_imei_number(request: HttpRequest) -> dict:
    initial = {}

    if request.method == "GET":
        imei_number = request.GET.get("imei", None)
        if imei_number:
            initial["imei_number"] = imei_number
            request.session["imei_number"] = imei_number

    elif request.method == "POST":
        if "imei_number" in request.POST:
            initial["imei_number"] = request.session["imei_number"]
            request.session["imei_number"] = request.POST.get("imei_number")

    return initial

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

class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label=_("First Name"),
        help_text=_("Please enter your first name."),
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label=_("Last Name"),
        help_text=_("Please enter your last name."),
    )
    email = forms.EmailField(
        max_length=255,
        required=True,
        label=_("Email"),
        help_text=_("Please enter your email address.")
    )
    password1 = forms.CharField(
        max_length=64,
        min_length=8,
        label=_("Password"),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        max_length=64,
        min_length=8,
        label=_("Confirm Password"),
        widget=forms.PasswordInput,
    )

    def clean(self, *args, **kwargs) -> dict:
        cleaned_data = super().clean(*args, **kwargs)

        password1 = cleaned_data["password1"]
        password2 = cleaned_data["password2"]

        if password1 != password2:
            self.add_error("password1", _("Passwords do not match."))
            self.add_error("password2", _("Passwords do not match."))

        return cleaned_data

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

class DriverForm(PersonForm, ContactForm):
    fields_order = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
    ]

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
        cleaned_data = super(RegistrationForm, self).clean()
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

        return cleaned_data

    def get_absolute_url(self):
        return reverse("/forms/registration/", kwargs={"pk": self.pk})

    def clean_imei_number(self) -> str:
        value = self.cleaned_data.get("imei_number")
        max_length = 20
        min_length = 12

        if not value:
            self.add_error(
                "imei_number",
                ValidationError(
                    _("This is required."),
                )
            )

        if not value.isdigit():
            self.add_error(
                "imei_number",
                ValidationError(
                    _("Can only contain digits.")
                )
            )

        if len(value) > max_length:
            self.add_error(
                "imei_number",
                ValidationError(
                    _("Must be less than '%(max_length)s' chars long. It has %(curr_length)s."),
                    params={"max_length": max_length, "curr_length": len(value)}
                )
            )

        if len(value) < min_length:
            self.add_error(
                "imei_number",
                ValidationError(
                    _("Must be greater than '%(min_length)s' chars long. It has %(curr_length)s."),
                    params={"min_length": min_length, "curr_length": len(value)}
                )
            )

        with WialonSession() as session:
            if not imei_number_exists_in_wialon(value, session):
                self.add_error(
                    "imei_number",
                    ValidationError(
                        _("'%(value)s' was not found in the TerminusGPS database. Please double-check your asset's IMEI #."),
                        params={"value": value}
                    )
               )
            if not imei_number_is_unregistered(value, session):
                self.add_error(
                    "imei_number",
                    ValidationError(
                        _("'%(value)s' is already registered with another user. Please double-check your asset's IMEI #."),
                        params={"value": value}
                    )
                )

        return value 
