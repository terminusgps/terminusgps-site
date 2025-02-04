from authorizenet.apicontractsv1 import creditCardType, customerAddressType
from django import forms

from .widgets import AddressWidget, CreditCardWidget


class AddressField(forms.MultiValueField):
    widget = AddressWidget

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(),  # Address First Name
            forms.CharField(),  # Address Last Name
            forms.CharField(),  # Address Street
            forms.CharField(),  # Address City
            forms.CharField(),  # Address State
            forms.CharField(),  # Address Country
            forms.CharField(),  # Address Zip Number
            forms.CharField(),  # Address Phone Number
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list) -> customerAddressType:
        return customerAddressType(
            firstName=data_list[0],
            lastName=data_list[1],
            address=data_list[2],
            city=data_list[3],
            state=data_list[4],
            country=data_list[5],
            zip=data_list[6],
            phoneNumber=data_list[7],
        )


class CreditCardField(forms.MultiValueField):
    widget = CreditCardWidget

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(),  # Credit Card Number
            forms.CharField(),  # Credit Card Expiry Month
            forms.CharField(),  # Credit Card Expiry Year
            forms.CharField(),  # Credit Card CCV
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list) -> creditCardType:
        return creditCardType(
            cardNumber=data_list[0],
            expirationDate=f"{data_list[1]}-20{data_list[2]}",
            cardCode=data_list[3],
        )
