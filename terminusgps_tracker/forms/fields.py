from typing import Collection
from django import forms


class AddressField(forms.MultiValueField):
    def __init__(self, **kwargs) -> None:
        countries = (("US", "United States"), ("CA", "Canada"), ("MX", "Mexico"))
        widget = kwargs.pop("widget", AddressWidget())
        fields = kwargs.pop(
            "fields",
            (
                forms.CharField(label="Street"),
                forms.CharField(label="City"),
                forms.CharField(label="State"),
                forms.CharField(label="Zip", min_length=5, max_length=9),
                forms.ChoiceField(label="Country", choices=countries),
                forms.CharField(label="Phone #", required=False),
            ),
        )
        super().__init__(widget=widget, fields=fields, **kwargs)


class CreditCardField(forms.MultiValueField):
    def __init__(self, **kwargs) -> None:
        widget = kwargs.pop("widget", CreditCardWidget())
        fields = kwargs.pop(
            "fields",
            (
                forms.CharField(label="Card #"),
                forms.CharField(label="Card Expiration", min_length=4, max_length=4),
                forms.CharField(label="Card CCV #", min_length=3, max_length=4),
            ),
        )
        super().__init__(widget=widget, fields=fields, **kwargs)


class AddressWidget(forms.MultiWidget):
    def __init__(self, **kwargs) -> None:
        widgets = kwargs.pop(
            "widgets",
            (
                forms.widgets.TextInput(),
                forms.widgets.TextInput(),
                forms.widgets.TextInput(),
                forms.widgets.TextInput(),
                forms.widgets.TextInput(),
                forms.widgets.TextInput(),
            ),
        )
        super().__init__(widgets=widgets, **kwargs)

    def decompress(self, value: str) -> list[str] | list[None]:
        if value:
            return value.split(",")
        return [None, None, None, None, None, None]


class CreditCardWidget(forms.MultiWidget):
    def __init__(self, **kwargs) -> None:
        widgets = kwargs.pop(
            "widgets",
            (
                forms.widgets.NumberInput(),
                forms.widgets.DateInput(),
                forms.widgets.NumberInput(),
            ),
        )
        super().__init__(widgets=widgets, **kwargs)

    def decompress(self, value: str) -> list[str] | list[None]:
        if value:
            return value.split(",")
        return [None, None, None, None, None, None]
