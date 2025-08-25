import datetime

from authorizenet import apicontractsv1
from django import forms


class AddressWidget(forms.widgets.MultiWidget):
    def decompress(self, value) -> list[str | None]:
        if value:
            return [
                value.firstName,
                value.lastName,
                value.phoneNumber,
                value.address,
                value.city,
                value.state,
                value.zip,
                value.country,
            ]
        return [None, None, None, None, None, None, None, None]


class AddressField(forms.MultiValueField):
    def compress(self, data_list) -> apicontractsv1.customerAddressType:
        return apicontractsv1.customerAddressType(
            firstName=data_list[0],
            lastName=data_list[1],
            phoneNumber=data_list[2],
            address=data_list[3],
            city=data_list[4],
            state=data_list[5],
            zip=data_list[6],
            country=data_list[7],
        )


class CreditCardWidget(forms.widgets.MultiWidget):
    def decompress(self, value) -> list[str | None]:
        if value:
            return [value.cardNumber, value.expirationDate, value.cardCode]
        return [None, None, None]


class CreditCardField(forms.MultiValueField):
    def compress(self, data_list) -> apicontractsv1.creditCardType:
        return apicontractsv1.creditCardType(
            cardNumber=data_list[0],
            expirationDate=data_list[1].strftime("%Y-%d"),
            cardCode=data_list[2],
        )


class ExpirationDateField(forms.MultiValueField):
    def compress(self, data_list):
        return datetime.datetime.strptime(
            f"{data_list[1]}-{data_list[0]}", "%Y-%d"
        )


class ExpirationDateWidget(forms.widgets.MultiWidget):
    def decompress(self, value) -> list[str | None]:
        if value:
            return [value.year, value.month]
        return [None, None]
