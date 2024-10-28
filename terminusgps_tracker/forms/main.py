from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.forms.renderers import TemplatesSetting
from django.template.base import Template
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from terminusgps_tracker.forms.fields import CreditCardField, AddressField
from terminusgps_tracker.forms.widgets import (
    CreditCardWidget,
    AddressWidget,
    TerminusTextInput,
    TerminusEmailInput,
    TerminusPasswordInput,
    TerminusNumberInput,
)
from terminusgps_tracker.validators import (
    validate_django_username,
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/forms/form.html"
    field_template_name = "terminusgps_tracker/forms/field.html"

    def get_template(self, template_name: str) -> Template | None:
        if settings.DEBUG:
            print(f"Getting template '{template_name}'...")
        return super().get_template(template_name)


class CustomerRegistrationForm(forms.Form):
    default_renderer = TerminusFormRenderer
    first_name = forms.CharField(
        label="First Name",
        min_length=4,
        max_length=64,
        widget=TerminusTextInput({"placeholder": "First"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        min_length=4,
        max_length=64,
        widget=TerminusTextInput({"placeholder": "Last"}),
    )
    email = forms.EmailField(
        label="Email Address",
        validators=[validate_wialon_username, validate_django_username],
        min_length=4,
        max_length=512,
        widget=TerminusEmailInput({"placeholder": "email@terminusgps.com"}),
    )
    password1 = forms.CharField(
        label="Password",
        validators=[validate_wialon_password],
        min_length=4,
        max_length=32,
        widget=TerminusPasswordInput(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=TerminusPasswordInput(),
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
        widget=TerminusTextInput({"placeholder": "My Vehicle"}),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=TerminusNumberInput({"placeholder": "123412341234"}),
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
        widget=CreditCardWidget(),
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
        widget=AddressWidget(),
    )
