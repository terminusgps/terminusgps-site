from typing import Collection

from django.db import models
from django.forms.widgets import MultiWidget, Select, TextInput
from django.utils.translation import gettext_lazy as _

from authorizenet.apicontractsv1 import creditCardType, customerAddressType


class AddressCountries(models.TextChoices):
    USA = "USA", _("United States")
    MEX = "Mexico", _("Mexico")
    CAN = "Canada", _("Canada")


class CreditCardWidget(MultiWidget):
    def __init__(
        self, widgets: Collection = (), field_class: str | None = None, **kwargs
    ) -> None:
        field_class = (
            field_class or "p-2 w-full border border-gray-600 rounded bg-gray-50"
        )
        if not widgets:
            widgets = {
                "number": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Card #",
                        "maxlength": 16,
                    }
                ),
                "expiry_month": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "MM",
                        "minlength": 2,
                        "maxlength": 2,
                    }
                ),
                "expiry_year": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "YY",
                        "minlength": 2,
                        "maxlength": 2,
                    }
                ),
                "ccv": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "CCV #",
                        "minlength": 3,
                        "maxlength": 4,
                    }
                ),
            }
        return super().__init__(widgets=widgets, **kwargs)

    def decompress(self, value: creditCardType | None):
        if value is None:
            return [None] * len(self.widgets)

        exp_month, exp_year = value.expirationDate.split("-")
        return {
            "number": value.cardNumber,
            "expiry_month": exp_month,
            "expiry_year": exp_year,
            "ccv": value.cardCode,
        }


class AddressWidget(MultiWidget):
    def __init__(
        self, widgets: Collection = (), field_class: str | None = None, **kwargs
    ) -> None:
        field_class = (
            field_class or "p-2 w-full border border-gray-600 rounded bg-gray-50"
        )
        if not widgets:
            widgets = {
                "first_name": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "First Name",
                        "maxlength": 64,
                    }
                ),
                "last_name": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Last Name",
                        "maxlength": 64,
                    }
                ),
                "street": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Street",
                        "maxlength": 128,
                    }
                ),
                "city": TextInput(
                    attrs={"class": field_class, "placeholder": "City", "maxlength": 64}
                ),
                "state": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "State",
                        "maxlength": 64,
                    }
                ),
                "country": Select(
                    attrs={
                        "class": field_class,
                        "placeholder": "Country",
                        "maxlength": 64,
                    },
                    choices=AddressCountries.choices,
                ),
                "zip": TextInput(
                    attrs={"class": field_class, "placeholder": "Zip #", "maxlength": 9}
                ),
                "phone": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Phone #",
                        "maxlength": 19,
                    }
                ),
            }
        return super().__init__(widgets=widgets, **kwargs)

    def decompress(self, value: customerAddressType | None):
        if value is None:
            return [None] * len(self.widgets)
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
