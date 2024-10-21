from typing import Any

from django import forms
from django.forms.renderers import TemplatesSetting
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.forms.validators import (
    validate_django_username,
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/forms/partials/_form.html"
    field_template_name = "terminusgps_tracker/forms/partials/_field.html"
    formset_template_name = "terminusgps_tracker/forms/partials/_formset.html"

    def get_template(self, template_name: str, **kwargs):
        if template_name.startswith("django/forms/widgets/"):
            template_name = template_name.replace(
                "django/forms/widgets/", "terminusgps_tracker/forms/partials/_"
            )
        elif template_name.startswith("django/forms/"):
            template_name = template_name.replace(
                "django/forms/", "terminusgps_tracker/forms/"
            )
        return super().get_template(template_name, **kwargs)


class CustomerRegistrationForm(forms.Form):
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

            if password and password_confirmation and password != password_confirmation:
                self.add_error(
                    "password1",
                    ValidationError(_("Passwords do not match."), code="invalid"),
                )
                self.add_error(
                    "password2",
                    ValidationError(_("Passwords do not match."), code="invalid"),
                )
        return cleaned_data


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(label="Password", widget=forms.widgets.PasswordInput())


class AssetCustomizationForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name", validators=[validate_wialon_unit_name], min_length=4
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=forms.widgets.NumberInput(),
    )
