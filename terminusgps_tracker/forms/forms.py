from typing import Any
from django import forms
from django.forms import widgets
from django.forms.renderers import TemplatesSetting
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.forms.widgets import TerminusAddressWidget
from terminusgps_tracker.forms.validators import (
    validate_asset_name_is_unique,
    validate_imei_number_is_available,
)


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/partials/_form.html"
    field_template_name = "terminusgps_tracker/partials/_field.html"
    formset_template_name = "terminusgps_tracker/partials/_formset.html"


class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name", max_length=64, widget=forms.TextInput()
    )
    last_name = forms.CharField(
        label="Last Name", max_length=64, widget=forms.TextInput()
    )
    phone_number = forms.CharField(label="Phone #", max_length=64)
    email = forms.EmailField(label="Email Address", widget=forms.EmailInput())
    password1 = forms.CharField(
        label="Password", max_length=32, min_length=8, widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label="Confirm Password",
        max_length=32,
        min_length=8,
        widget=forms.PasswordInput(),
    )

    def _set_field_attrs(self) -> None:
        err_attrs: dict = {
            "class": "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
        }
        ok_attrs: dict = {
            "class": "bg-green-50 border border-green-500 text-green-900 dark:text-green-400 placeholder-green-700 dark:placeholder-green-500 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block w-full p-2.5 dark:bg-gray-700 dark:border-green-500"
        }
        unbound_attrs: dict = {
            "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        }

        for field_name in self.fields:
            if not self.is_bound:
                self.fields[field_name].widget.attrs.update(unbound_attrs)
            elif field_name in self.errors:
                self.fields[field_name].widget.attrs.update(err_attrs)
            else:
                self.fields[field_name].widget.attrs.update(ok_attrs)

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
        self._set_field_attrs()
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

    def clean(self, **kwargs) -> dict[str, Any] | None:
        for field_name in self.fields:
            if self.errors and field_name in self.errors:
                self.set_invalid(field_name)
            else:
                self.set_valid(field_name)
        return super().clean(**kwargs)

    def set_invalid(self, field_name: str) -> None:
        self.fields[field_name].widget.attrs.update(
            {
                "class": "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
            }
        )

    def set_valid(self, field_name: str) -> None:
        self.fields[field_name].widget.attrs.update(
            {
                "class": "bg-green-50 border border-green-500 text-green-900 dark:text-green-400 placeholder-green-700 dark:placeholder-green-500 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block w-full p-2.5 dark:bg-gray-700 dark:border-green-500"
            }
        )


class CustomerCreditCardUploadForm(forms.Form):
    card_number = forms.CharField(label="Card #", min_length=8, max_length=19)
    card_expiry = forms.CharField(label="Card Expiration", min_length=2, max_length=2)
    card_code = forms.CharField(label="Card Security Code", min_length=2, max_length=4)

    address = forms.MultiValueField(
        fields=(
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Zip"),
            forms.CharField(label="Country"),
            forms.CharField(label="Phone #"),
        ),
        widget=TerminusAddressWidget(
            widgets=(
                widgets.TextInput(),
                widgets.TextInput(),
                widgets.TextInput(),
                widgets.TextInput(),
                widgets.TextInput(),
                widgets.TextInput(),
            )
        ),
    )

    def clean(self, **kwargs) -> dict[str, Any] | None:
        [self.update_attr(field_name) for field_name in self.fields]
        return super().clean(**kwargs)

    def update_attr(self, field_name: str) -> None:
        if self.errors and field_name in self.errors:
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
                }
            )
        else:
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "bg-green-50 border border-green-500 text-green-900 dark:text-green-400 placeholder-green-700 dark:placeholder-green-500 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block w-full p-2.5 dark:bg-gray-700 dark:border-green-500"
                }
            )
