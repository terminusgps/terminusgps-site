from typing import Collection

from django.db import models
from django.forms.widgets import MultiWidget, NumberInput, Select, TextInput
from django.utils.translation import gettext_lazy as _

from authorizenet.apicontractsv1 import creditCardType, customerAddressType


class AddressCountries(models.TextChoices):
    USA = "USA", _("United States")
    MEX = "Mexico", _("Mexico")
    CAN = "Canada", _("Canada")


class AddressWidget(MultiWidget):
    def __init__(
        self,
        widgets: Collection = (),
        field_class: str = "p-2 w-full border border-gray-600 rounded bg-gray-50",
        **kwargs,
    ) -> None:
        if not widgets:
            widgets = {
                "street": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Street",
                        "maxlength": 64,
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
                    attrs={
                        "class": field_class,
                        "placeholder": "Zip #",
                        "minlength": 5,
                        "maxlength": 10,
                        "pattern": "^(?:\\d{4}-\\d{5}|\\d{5})$",
                    }
                ),
            }
        return super().__init__(widgets=widgets, **kwargs)

    def decompress(self, value: customerAddressType | None):
        if value is None:
            return [None] * len(self.widgets)

        return {
            "street": value.address,
            "city": value.city,
            "state": value.state,
            "country": value.country,
            "zip": value.zip,
        }


class ExpirationDateWidget(MultiWidget):
    def decompress(self, value: creditCardType | None):
        if value is None:
            return [None] * len(self.widgets)

        exp_parts = value.expirationDate.split("-")
        month, year = exp_parts[0], exp_parts[1][2:]
        return {"month": month, "year": year}


class CreditCardWidget(MultiWidget):
    def __init__(
        self,
        widgets: Collection = (),
        field_class: str = "p-2 w-full border border-gray-600 rounded bg-gray-50",
        **kwargs,
    ) -> None:
        if not widgets:
            widgets = {
                "number": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Card #",
                        "minlength": 15,
                        "maxlength": 19,
                    }
                ),
                "expiry": ExpirationDateWidget(
                    widgets={
                        "month": NumberInput(
                            attrs={
                                "class": field_class,
                                "placeholder": "MM",
                                "minlength": 2,
                                "maxlength": 2,
                            }
                        ),
                        "year": NumberInput(
                            attrs={
                                "class": field_class,
                                "placeholder": "YY",
                                "minlength": 2,
                                "maxlength": 2,
                            }
                        ),
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

        return {
            "number": value.cardNumber,
            "expiry": value.expirationDate,
            "ccv": value.cardCode,
        }


class BillingAddressWidget(MultiWidget):
    def __init__(
        self,
        widgets: Collection = (),
        field_class: str = "p-2 w-full border border-gray-600 rounded bg-gray-50",
        **kwargs,
    ) -> None:
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
                "phone": TextInput(
                    attrs={
                        "class": field_class,
                        "placeholder": "Phone #",
                        "maxlength": 19,
                    }
                ),
                "address": AddressWidget(),
            }
        return super().__init__(widgets=widgets, **kwargs)

    def decompress(self, value: customerAddressType | None):
        if value is None:
            return [None] * len(self.widgets)

        return {
            "first_name": value.firstName,
            "last_name": value.lastName,
            "phone": value.phoneNumber,
            "address": {
                "street": value.address,
                "city": value.city,
                "state": value.state,
                "country": value.country,
                "zip": value.zip,
            },
        }


class ShippingAddressWidget(BillingAddressWidget):
    pass
