import datetime

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    Subscription,
)

from .models import WialonUnit

WIDGET_CSS_CLASS = getattr(
    settings,
    "WIDGET_CSS_CLASS",
    "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-valid:bg-green-50 user-valid:text-green-700 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
)


class WialonUnitCreateForm(forms.ModelForm):
    imei = forms.CharField(
        label=_("IMEI #"),
        help_text=_("Enter the IMEI number found on your installed device."),
        max_length=25,
        widget=forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "4111111111111111",
                "enterkeyhint": "done",
                "inputmode": "numeric",
                "aria-required": "true",
                "autocapitalize": "off",
                "autocorrect": "off",
            }
        ),
    )

    class Meta:
        model = WialonUnit
        fields = ["name"]
        help_texts = {"name": _("Enter a name for your GPS-tracked asset.")}
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "minlength": "4",
                    "maxlength": "50",
                    "placeholder": "New Ride",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocorrect": "on",
                    "required": True,
                }
            )
        }

    def clean(self):
        super().clean()
        err = ValidationError(_("This field is required."), code="invalid")
        if not self.cleaned_data.get("name"):
            self.add_error("name", err)
        if not self.cleaned_data.get("imei"):
            self.add_error("imei", err)


class ExpirationDateWidget(forms.widgets.MultiWidget):
    def __init__(self, **kwargs) -> None:
        return super().__init__(**kwargs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]


class ExpirationDateField(forms.MultiValueField):
    def __init__(self, fields=(), widget=None, **kwargs) -> None:
        return super().__init__(
            error_messages={},
            fields=(
                forms.DateField(input_formats=["%m", "%-m"]),
                forms.DateField(input_formats=["%y"]),
            ),
            widget=widget,
            require_all_fields=False,
            **kwargs,
        )

    def compress(self, data_list):
        if data_list:
            return datetime.date(
                day=1, month=data_list[0].month, year=data_list[1].year
            )
        return None


class SubscriptionCreateForm(forms.ModelForm):
    consent = forms.BooleanField(
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )

    class Meta:
        model = Subscription
        fields = ["pprofile", "aprofile"]
        widgets = {
            "pprofile": forms.widgets.Select(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "enterkeyhint": "next",
                    "aria-required": "true",
                }
            ),
            "aprofile": forms.widgets.Select(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "enterkeyhint": "next",
                    "aria-required": "true",
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["pprofile"].empty_label = None
        self.fields["aprofile"].empty_label = None


class CustomerAddressProfileCreateForm(forms.ModelForm):
    class Meta:
        model = CustomerAddressProfile
        fields = [
            "first_name",
            "last_name",
            "company_name",
            "address",
            "city",
            "state",
            "country",
            "zip",
            "phone_number",
        ]
        help_texts = {
            "first_name": _("Enter a first name."),
            "last_name": _("Enter a last name."),
            "company_name": _("Optional. Enter a company name."),
            "address": _("Enter a house number + street."),
            "city": _("Enter a city."),
            "state": _("Enter a state."),
            "zip": _("Enter a ZIP code."),
            "country": _("Enter a country."),
            "phone_number": _(
                "Optional. Enter an E.164-formatted phone number. Ex: 17139045262"
            ),
        }
        widgets = {
            "first_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "50",
                    "placeholder": "First",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "shipping given-name",
                    "autocorrect": "off",
                    "autofocus": True,
                }
            ),
            "last_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "50",
                    "placeholder": "Last",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "shipping family-name",
                    "autocorrect": "off",
                }
            ),
            "company_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "50",
                    "placeholder": "Terminus GPS",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "false",
                    "autocapitalize": "words",
                    "autocomplete": "shipping organization",
                    "autocorrect": "off",
                }
            ),
            "address": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "60",
                    "placeholder": "17610 South Dr",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "shipping street-address",
                    "autocorrect": "off",
                }
            ),
            "city": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "40",
                    "placeholder": "Cypress",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "shipping address-level2",
                    "autocorrect": "off",
                }
            ),
            "state": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "40",
                    "placeholder": "TX",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "shipping address-level1",
                    "autocorrect": "off",
                }
            ),
            "country": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "60",
                    "placeholder": "USA",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "shipping country",
                    "autocorrect": "off",
                }
            ),
            "zip": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "20",
                    "placeholder": "77433",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "shipping postal-code",
                    "autocorrect": "off",
                }
            ),
            "phone_number": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "25",
                    "placeholder": "17139045262",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "false",
                    "autocomplete": "shipping tel",
                    "autocorrect": "off",
                    "pattern": "[0-9]{0,20}",
                }
            ),
        }

    def clean(self):
        super().clean()
        address_fields = {
            "first_name": self.cleaned_data.get("first_name"),
            "last_name": self.cleaned_data.get("last_name"),
            "company_name": self.cleaned_data.get("company_name"),
            "address": self.cleaned_data.get("address"),
            "city": self.cleaned_data.get("city"),
            "state": self.cleaned_data.get("state"),
            "country": self.cleaned_data.get("country"),
            "zip": self.cleaned_data.get("zip"),
            "phone_number": self.cleaned_data.get("phone_number"),
        }
        if not all(address_fields.values()):
            for field, val in address_fields.items():
                if not val and field not in ("company_name", "phone_number"):
                    self.add_error(
                        field,
                        ValidationError(
                            _("This field is required."), code="invalid"
                        ),
                    )


class CustomerPaymentProfileCreateForm(forms.ModelForm):
    class Meta:
        model = CustomerPaymentProfile
        field_classes = {"expiry_date": ExpirationDateField}
        fields = [
            "first_name",
            "last_name",
            "company_name",
            "address",
            "city",
            "state",
            "country",
            "zip",
            "phone_number",
            "card_number",
            "expiry_date",
            "card_code",
            "account_number",
            "routing_number",
            "account_name",
            "bank_name",
            "account_type",
        ]
        help_texts = {
            "first_name": _("Enter a first name."),
            "last_name": _("Enter a last name."),
            "company_name": _("Optional. Enter a company name."),
            "address": _("Enter a house number + street."),
            "city": _("Enter a city."),
            "state": _("Enter a state."),
            "zip": _("Enter a ZIP code."),
            "country": _("Enter a country."),
            "phone_number": _(
                "Optional. Enter an E.164-formatted phone number. Ex: 17139045262"
            ),
            "card_number": _("Enter a card number."),
            "expiry_date": _("Enter an expiration date month and year."),
            "card_code": _("Enter a 3-4 digit CCV code."),
            "account_number": _("Enter an account number."),
            "routing_number": _("Enter a routing number."),
            "account_name": _("Enter an account holder name."),
            "bank_name": _("Enter a bank name."),
            "account_type": _("Select a bank account type."),
        }
        widgets = {
            "first_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "First",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "billing given-name",
                    "autocorrect": "off",
                    "autofocus": True,
                }
            ),
            "last_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Last",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "billing family-name",
                    "autocorrect": "off",
                }
            ),
            "company_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Terminus GPS",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "false",
                    "autocapitalize": "words",
                    "autocomplete": "billing organization",
                    "autocorrect": "off",
                }
            ),
            "address": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "17610 South Dr",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "billing street-address",
                    "autocorrect": "off",
                }
            ),
            "city": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Cypress",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "billing address-level2",
                    "autocorrect": "off",
                }
            ),
            "state": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "TX",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "characters",
                    "autocomplete": "billing address-level1",
                    "autocorrect": "off",
                }
            ),
            "country": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "60",
                    "placeholder": "USA",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "billing country",
                    "autocorrect": "off",
                }
            ),
            "zip": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "20",
                    "placeholder": "77433",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocapitalize": "none",
                    "autocomplete": "billing postal-code",
                    "autocorrect": "off",
                }
            ),
            "phone_number": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "25",
                    "placeholder": "17139045262",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "false",
                    "autocapitalize": "none",
                    "autocomplete": "billing tel",
                    "autocorrect": "off",
                    "pattern": "[0-9]{0,20}",
                }
            ),
            "card_number": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "minlength": "13",
                    "maxlength": "16",
                    "placeholder": "4111111111111111",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocapitalize": "none",
                    "autocomplete": "cc-number",
                    "autocorrect": "off",
                }
            ),
            "expiry_date": ExpirationDateWidget(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "maxlength": "2",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocapitalize": "none",
                    "autocorrect": "off",
                },
                widgets={
                    "month": forms.widgets.DateInput(
                        format="%m",
                        attrs={
                            "minlength": "1",
                            "placeholder": "MM",
                            "autocomplete": "cc-exp-month",
                        },
                    ),
                    "year": forms.widgets.DateInput(
                        format="%y",
                        attrs={
                            "minlength": "2",
                            "placeholder": "YY",
                            "autocomplete": "cc-exp-year",
                        },
                    ),
                },
            ),
            "card_code": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "minlength": "3",
                    "maxlength": "4",
                    "placeholder": "444",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "false",
                    "autocapitalize": "none",
                    "autocomplete": "cc-csc",
                    "autocorrect": "off",
                }
            ),
            "account_number": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "41111111111111111",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocapitalize": "none",
                    "autocomplete": "cc-number",
                    "autocorrect": "off",
                }
            ),
            "routing_number": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "411111111",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocapitalize": "none",
                    "autocomplete": "cc-number",
                    "autocorrect": "off",
                }
            ),
            "account_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Terminus GPS",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "cc-name",
                    "autocorrect": "off",
                }
            ),
            "bank_name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Wells Fargo",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocapitalize": "words",
                    "autocomplete": "cc-name",
                    "autocorrect": "off",
                }
            ),
            "account_type": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS, "aria-required": "true"}
            ),
        }

    def clean(self):
        super().clean()

        address_fields = {
            "first_name": self.cleaned_data.get("first_name"),
            "last_name": self.cleaned_data.get("last_name"),
            "company_name": self.cleaned_data.get("company_name"),
            "address": self.cleaned_data.get("address"),
            "city": self.cleaned_data.get("city"),
            "state": self.cleaned_data.get("state"),
            "country": self.cleaned_data.get("country"),
            "zip": self.cleaned_data.get("zip"),
            "phone_number": self.cleaned_data.get("phone_number"),
        }
        credit_card_fields = {
            "card_number": self.cleaned_data.get("card_number"),
            "expiry_date": self.cleaned_data.get("expiry_date"),
            "card_code": self.cleaned_data.get("card_code"),
        }
        bank_account_fields = {
            "account_number": self.cleaned_data.get("account_number"),
            "routing_number": self.cleaned_data.get("routing_number"),
            "account_name": self.cleaned_data.get("account_name"),
            "bank_name": self.cleaned_data.get("bank_name"),
            "account_type": self.cleaned_data.get("account_type"),
        }

        if not all(address_fields.values()):
            for field, val in address_fields.items():
                if not val and field not in ("company_name", "phone_number"):
                    self.add_error(
                        field,
                        ValidationError(
                            _("This field is required."), code="invalid"
                        ),
                    )
        if not any(credit_card_fields.values()) and not any(
            bank_account_fields.values()
        ):
            self.add_error(
                None,
                ValidationError(
                    _("Credit card or bank account is required."),
                    code="invalid",
                ),
            )
        if any(bank_account_fields.values()):
            if not all(bank_account_fields.values()):
                for field in bank_account_fields.keys():
                    self.add_error(
                        field,
                        ValidationError(
                            _("This field is required."), code="invalid"
                        ),
                    )
        if any(credit_card_fields.values()):
            if not all(credit_card_fields.values()):
                for field in credit_card_fields.keys():
                    self.add_error(
                        field,
                        ValidationError(
                            _("This field is required."), code="invalid"
                        ),
                    )
            if expiry := self.cleaned_data.get("expiry_date"):
                if expiry < datetime.date.today():
                    self.add_error(
                        "expiry_date",
                        ValidationError(
                            _("Expiration date must be in the future."),
                            code="invalid",
                        ),
                    )
