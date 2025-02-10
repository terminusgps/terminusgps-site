from authorizenet.apicontractsv1 import creditCardType, customerAddressType
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator

from terminusgps_tracker.validators import validate_credit_card_number

from .widgets import (
    AddressWidget,
    CreditCardWidget,
    ShippingAddressWidget,
    BillingAddressWidget,
)


class AddressField(forms.MultiValueField):
    widget = AddressWidget

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Country"),
            forms.CharField(label="Zip #"),
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list):
        return {
            "street": data_list[0],
            "city": data_list[1],
            "state": data_list[2],
            "country": data_list[3],
            "zip": data_list[4],
        }


class BillingAddressField(forms.MultiValueField):
    widget = BillingAddressWidget

    def __init__(self, addr_label: str = "Billing Address", **kwargs) -> None:
        fields = (
            forms.CharField(label="First Name"),
            forms.CharField(label="Last Name"),
            forms.CharField(label="Phone #"),
            AddressField(label=addr_label),
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list) -> customerAddressType:
        addr_dict = data_list[3]
        return customerAddressType(
            firstName=data_list[0],
            lastName=data_list[1],
            address=addr_dict["street"],
            city=addr_dict["city"],
            state=addr_dict["state"],
            country=addr_dict["country"],
            zip=addr_dict["zip"],
            phoneNumber=data_list[2],
        )


class ShippingAddressField(forms.MultiValueField):
    widget = ShippingAddressWidget

    def __init__(self, addr_label: str = "Shipping Address", **kwargs) -> None:
        fields = (
            forms.CharField(label="First Name"),
            forms.CharField(label="Last Name"),
            forms.CharField(label="Phone #"),
            AddressField(label=addr_label),
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list) -> customerAddressType:
        addr_dict = data_list[3]
        return customerAddressType(
            firstName=data_list[0],
            lastName=data_list[1],
            address=addr_dict["street"],
            city=addr_dict["city"],
            state=addr_dict["state"],
            country=addr_dict["country"],
            zip=addr_dict["zip"],
            phoneNumber=data_list[2],
        )


class CreditCardField(forms.MultiValueField):
    widget = CreditCardWidget

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(
                label="Card #",
                validators=[MaxLengthValidator(16), validate_credit_card_number],
            ),
            forms.CharField(
                label="Card Expiration Month",
                validators=[MinLengthValidator(2), MaxLengthValidator(2)],
            ),
            forms.CharField(
                label="Card Expiration Year",
                validators=[MinLengthValidator(2), MaxLengthValidator(2)],
            ),
            forms.CharField(
                label="Card CCV #",
                validators=[MinLengthValidator(3), MaxLengthValidator(4)],
            ),
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list) -> creditCardType:
        return creditCardType(
            cardNumber=data_list[0],
            expirationDate=f"{data_list[1]}-20{data_list[2]}",
            cardCode=data_list[3],
        )
