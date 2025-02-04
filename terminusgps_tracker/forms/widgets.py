from authorizenet.apicontractsv1 import creditCardType, customerAddressType
from django.forms.widgets import MultiWidget, Select, TextInput
from django.db import models
from django.utils.translation import gettext_lazy as _


class AddressCountries(models.TextChoices):
    USA = "USA", _("United States")
    MEX = "Mexico", _("Mexico")
    CAN = "Canada", _("Canada")


class CreditCardWidget(MultiWidget):
    def __init__(
        self,
        widgets=(),
        base_css_class="p-2 w-full border border-gray-600 rounded bg-gray-50",
        **kwargs,
    ) -> None:
        if not widgets:
            widgets = {
                "number": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "Card #",
                        "maxlength": 16,
                    }
                ),
                "expiry_month": TextInput(
                    attrs={"class": base_css_class, "placeholder": "MM", "maxlength": 2}
                ),
                "expiry_year": TextInput(
                    attrs={"class": base_css_class, "placeholder": "YY", "maxlength": 2}
                ),
                "ccv": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "CCV #",
                        "maxlength": 4,
                    }
                ),
            }
        return super().__init__(widgets, **kwargs)

    def decompress(self, value: creditCardType | None):
        if value:
            exp_month, exp_year = value.expirationDate.split("-")
            return {
                "number": value.cardNumber,
                "expiry_month": exp_month,
                "expiry_year": exp_year,
                "ccv": value.cardCode,
            }
        return [None] * 4


class AddressWidget(MultiWidget):
    def __init__(
        self,
        widgets=(),
        base_css_class: str = "p-2 w-full border border-gray-600 rounded bg-gray-50",
        **kwargs,
    ) -> None:
        if not widgets:
            widgets = {
                "first_name": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "First Name",
                        "maxlength": 64,
                    }
                ),
                "last_name": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "Last Name",
                        "maxlength": 64,
                    }
                ),
                "street": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "Street",
                        "maxlength": 128,
                    }
                ),
                "city": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "City",
                        "maxlength": 64,
                    }
                ),
                "state": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "State",
                        "maxlength": 64,
                    }
                ),
                "country": Select(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "Country",
                        "maxlength": 64,
                    },
                    choices=AddressCountries.choices,
                ),
                "zip": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "Zip #",
                        "maxlength": 9,
                    }
                ),
                "phone": TextInput(
                    attrs={
                        "class": base_css_class,
                        "placeholder": "Phone #",
                        "maxlength": 19,
                    }
                ),
            }
        return super().__init__(widgets, **kwargs)

    def decompress(self, value: customerAddressType | None):
        if value:
            return {
                "first_name": value.firstName,
                "last_name": value.lastName,
                "street": value.address,
                "city": value.city,
                "state": value.state,
                "country": value.country,
                "zip": value.zip,
                "phone": value.phoneNumber,
            }
        return [None] * 8
