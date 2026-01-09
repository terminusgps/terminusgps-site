import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    Subscription,
)


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
    consent = forms.BooleanField(initial=False)

    class Meta:
        model = Subscription
        fields = ["pprofile", "aprofile"]
        widgets = {
            "pprofile": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 valid:bg-green-50 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "enterkeyhint": "next",
                    "aria-required": "true",
                }
            ),
            "aprofile": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 valid:bg-green-50 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
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
            "address": _("Enter a house number + street. Ex: 123 Main St"),
            "city": _("Enter a city name."),
            "state": _("Enter a state mailing code."),
            "zip": _("Enter a ZIP code."),
            "country": _("Enter a valid country."),
            "phone_number": _(
                "Optional. Enter an E.164-formatted phone number. Ex: 17139045262"
            ),
        }
        widgets = {
            "first_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 valid:bg-green-50 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "First",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autofocus": "on",
                    "autocomplete": "name",
                }
            ),
            "last_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Last",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "name",
                }
            ),
            "company_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Terminus GPS",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "false",
                    "autocomplete": "organization",
                }
            ),
            "address": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "17610 South Dr",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "street-address",
                }
            ),
            "city": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Cypress",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "address-level2",
                }
            ),
            "state": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "TX",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "address-level1",
                }
            ),
            "country": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "60",
                    "placeholder": "USA",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "country",
                }
            ),
            "zip": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "20",
                    "placeholder": "77433",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "postal-code",
                }
            ),
            "phone_number": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "20",
                    "placeholder": "17139045262",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "false",
                    "autocomplete": "tel",
                }
            ),
        }

    def clean(self):
        super().clean()
        required_fields = [
            "first_name",
            "last_name",
            "address",
            "city",
            "state",
            "country",
            "zip",
        ]
        for field in required_fields:
            if not self.cleaned_data[field]:
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
            "address": _("Enter a house number + street. Ex: 123 Main St"),
            "city": _("Enter a city name."),
            "state": _("Enter a state mailing code."),
            "zip": _("Enter a ZIP code."),
            "country": _("Enter a valid country."),
            "phone_number": _(
                "Optional. Enter an E.164-formatted phone number. Ex: 17139045262"
            ),
            "card_number": _("Enter a card number."),
            "expiry_date": _("Enter an expiration date month and year."),
            "card_code": _("Enter a 3-4 digit CCV code."),
            "account_number": _("Enter an account number."),
            "routing_number": _("Enter a routing number."),
            "account_name": _("Enter the name on the bank account."),
            "bank_name": _("Enter a bank name."),
            "account_type": _("Select a bank account type."),
        }
        widgets = {
            "first_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 valid:bg-green-50 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "First",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "name",
                    "autofocus": "on",
                }
            ),
            "last_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Last",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "name",
                }
            ),
            "company_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Terminus GPS",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "false",
                    "autocomplete": "organization",
                }
            ),
            "address": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "17610 South Dr",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "address-street",
                }
            ),
            "city": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Cypress",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "address-level2",
                }
            ),
            "state": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "TX",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "address-level1",
                }
            ),
            "country": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "60",
                    "placeholder": "USA",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "country",
                }
            ),
            "zip": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "20",
                    "placeholder": "77433",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "postal-code",
                }
            ),
            "phone_number": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "20",
                    "placeholder": "17139045262",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "false",
                    "autocomplete": "tel",
                }
            ),
            "card_number": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "minlength": "16",
                    "maxlength": "19",
                    "placeholder": "4111111111111111",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "cc-number",
                }
            ),
            "expiry_date": ExpirationDateWidget(
                widgets={
                    "month": forms.widgets.DateInput(
                        format="%m",
                        attrs={
                            "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                            "minlength": "1",
                            "maxlength": "2",
                            "placeholder": datetime.date.today().strftime(
                                "%m"
                            ),
                            "enterkeyhint": "next",
                            "inputmode": "numeric",
                            "aria-required": "true",
                            "autocomplete": "cc-exp-month",
                        },
                    ),
                    "year": forms.widgets.DateInput(
                        format="%y",
                        attrs={
                            "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                            "minlength": "2",
                            "maxlength": "2",
                            "placeholder": datetime.date.today().strftime(
                                "%y"
                            ),
                            "enterkeyhint": "next",
                            "inputmode": "numeric",
                            "aria-required": "true",
                            "autocomplete": "cc-exp-year",
                        },
                    ),
                }
            ),
            "card_code": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "minlength": "3",
                    "maxlength": "4",
                    "placeholder": "444",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "cc-csc",
                }
            ),
            "account_number": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "17",
                    "placeholder": "41111111111111111",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "cc-number",
                }
            ),
            "routing_number": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "9",
                    "placeholder": "411111111",
                    "enterkeyhint": "next",
                    "inputmode": "numeric",
                    "aria-required": "true",
                    "autocomplete": "cc-number",
                }
            ),
            "account_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "22",
                    "placeholder": "Terminus GPS",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "cc-name",
                }
            ),
            "bank_name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "maxlength": "50",
                    "placeholder": "Wells Fargo",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                    "aria-required": "true",
                    "autocomplete": "organization",
                }
            ),
            "account_type": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
                    "aria-required": "true",
                }
            ),
        }

    def clean(self):
        super().clean()
        if expiry := self.cleaned_data["expiry_date"]:
            if expiry < datetime.date.today():
                self.add_error(
                    "expiry_date",
                    ValidationError(
                        _("Expiration date must be in the future."),
                        code="invalid",
                    ),
                )
        if self.cleaned_data.get("account_type"):
            if not all(
                [
                    self.cleaned_data.get("account_number"),
                    self.cleaned_data.get("routing_number"),
                    self.cleaned_data.get("account_name"),
                    self.cleaned_data.get("bank_name"),
                ]
            ):
                self.cleaned_data["account_type"] = ""
