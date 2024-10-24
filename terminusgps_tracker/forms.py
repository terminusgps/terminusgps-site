from typing import Any, Collection

from django import forms
from django.forms import widgets
from django.db import models
from django.core.exceptions import ValidationError
from django.forms.renderers import TemplatesSetting
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.validators import (
    validate_django_username,
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class TerminusTextInput(widgets.TextInput):
    template_name = "terminusgps_tracker/forms/widgets/text.html"


class TerminusSelectInput(widgets.Select):
    template_name = "terminusgps_tracker/forms/widgets/select.html"


class TerminusInput(widgets.Input):
    template_name = "terminusgps_tracker/forms/widgets/input.html"


class TerminusNumberInput(widgets.NumberInput):
    template_name = "terminusgps_tracker/forms/widgets/number.html"


class CreditCardWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/multiwidget.html"

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["number", "expiry", "ccv"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/multiwidget.html"

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)


class CreditCardField(forms.MultiValueField):
    def compress(self, data_list: Collection) -> dict[str, Any]:
        data_keys = ["number", "expiry", "ccv"]
        if data_list:
            return dict(zip(data_keys, data_list))
        return dict(zip(data_keys, [None] * len(data_keys)))


class AddressField(forms.MultiValueField):
    def compress(self, data_list: Collection) -> dict[str, Any]:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if data_list:
            return dict(zip(data_keys, data_list))
        return dict(zip(data_keys, [None] * 6))


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/forms/form.html"
    field_template_name = "terminusgps_tracker/forms/field.html"


class CountryCode(models.TextChoices):
    US = "US", _("United States")
    CA = "CA", _("Canada")
    MX = "MX", _("Mexico")


class CustomerRegistrationForm(forms.Form):
    default_renderer = TerminusFormRenderer
    first_name = forms.CharField(label="First Name", min_length=4, max_length=64)
    last_name = forms.CharField(label="Last Name", min_length=4, max_length=64)
    email = forms.EmailField(
        label="Email Address",
        validators=[validate_wialon_username, validate_django_username],
        min_length=4,
        max_length=512,
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.widgets.PasswordInput(),
        validators=[validate_wialon_password],
        min_length=4,
        max_length=32,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.widgets.PasswordInput(),
        min_length=4,
        max_length=32,
    )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean()
        if cleaned_data:
            password = cleaned_data.get("password1")
            password_confirmation = cleaned_data.get("password2")

            if password and password_confirmation:
                if len(password) < 4:
                    error = ValidationError(
                        _("Password must be at least 4 chars in length. Got '%(len)s'"),
                        code="invalid",
                        params={"len": len(password)},
                    )
                    self.add_error("password1", error)
                    self.add_error("password2", error)
                elif password != password_confirmation:
                    error = ValidationError(
                        _("Passwords do not match."), code="invalid"
                    )
                    self.add_error("password1", error)
                    self.add_error("password2", error)
        return cleaned_data


class AssetCustomizationForm(forms.Form):
    default_renderer = TerminusFormRenderer
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=forms.widgets.NumberInput(),
        min_length=15,
        max_length=24,
    )


class CreditCardUploadForm(forms.Form):
    default_renderer = TerminusFormRenderer
    credit_card = CreditCardField(
        label="Credit Card",
        require_all_fields=True,
        fields=(
            forms.CharField(label="Card Number"),
            forms.CharField(label="Card Expiration"),
            forms.CharField(label="Card CCV #"),
        ),
        widget=CreditCardWidget(
            widgets={
                "number": TerminusTextInput(),
                "expiry": TerminusTextInput(),
                "ccv": TerminusTextInput(),
            }
        ),
    )
    address = AddressField(
        label="Address",
        require_all_fields=False,
        fields=(
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Zip"),
            forms.ChoiceField(label="Country"),
            forms.CharField(label="Phone #"),
        ),
        widget=AddressWidget(
            widgets={
                "street": TerminusTextInput(),
                "city": TerminusTextInput(),
                "state": TerminusTextInput(),
                "zip": TerminusTextInput(),
                "country": TerminusSelectInput(choices=CountryCode.choices),
                "phone": TerminusTextInput(),
            }
        ),
    )
